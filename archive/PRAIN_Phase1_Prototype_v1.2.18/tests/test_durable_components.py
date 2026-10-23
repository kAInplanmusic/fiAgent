import tempfile, unittest
from pathlib import Path
from prain import (DurableGoalRegistry, DurableEventBus, DurableEvidenceLedger,
                   Event, PRAINRuntime, Observation, GoalError)

class DurableComponentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.tmp.name) / 'runtime.sqlite3')
    def tearDown(self): self.tmp.cleanup()

    def test_goal_persists_and_transitions_after_restart(self):
        goals=DurableGoalRegistry(self.db)
        goals.create('persist me',[{'id':'c1','check':'healthy'}],'g1')
        goals.activate('g1')
        restarted=DurableGoalRegistry(self.db)
        self.assertEqual(restarted.get('g1').status,'active')
        done=restarted.record_verification('g1',True,['evidence://test/1'],'unit-test')
        self.assertEqual(done.status,'completed')
        with self.assertRaises(GoalError): restarted.activate('g1')

    def test_event_log_and_consumer_dedup_persist(self):
        seen=[]; bus=DurableEventBus(self.db)
        bus.subscribe('demo','consumer',lambda e: seen.append(e.event_id))
        event=Event.create('demo',{'v':1},event_id='event-1')
        self.assertEqual(bus.publish(event)['consumer'],'processed')
        restarted=DurableEventBus(self.db); restarted.subscribe('demo','consumer',lambda e: seen.append('unexpected'))
        self.assertEqual(restarted.publish(event)['consumer'],'duplicate_ignored')
        self.assertEqual(seen,['event-1'])
        self.assertEqual(restarted.events()[0].event_id,'event-1')

    def test_event_handler_failure_is_unknown_and_not_blindly_retried(self):
        bus = DurableEventBus(self.db)
        calls = []
        bus.subscribe('work', 'worker', lambda event: (calls.append(event.event_id), (_ for _ in ()).throw(TimeoutError('ambiguous'))))
        event = Event.create('work', {'x': 1}, event_id='ambiguous-event')
        with self.assertRaises(TimeoutError):
            bus.publish(event)
        self.assertEqual(bus.delivery_status('work','worker','ambiguous-event')['status'], 'OUTCOME_UNKNOWN')
        restarted = DurableEventBus(self.db)
        restarted.subscribe('work','worker',lambda e: calls.append('must-not-run'))
        self.assertEqual(restarted.publish(event)['worker'], 'outcome_unknown')
        self.assertEqual(calls, ['ambiguous-event'])

    def test_event_delivery_reconciles_only_with_evidence(self):
        bus = DurableEventBus(self.db)
        bus.subscribe('work','worker',lambda e: (_ for _ in ()).throw(TimeoutError('unknown')))
        event = Event.create('work', {}, event_id='reconcile-event')
        with self.assertRaises(TimeoutError): bus.publish(event)
        with self.assertRaises(ValueError):
            bus.reconcile_delivery('work','worker',event.event_id,'NOT_EXECUTED',' ')
        state = bus.reconcile_delivery('work','worker',event.event_id,'NOT_EXECUTED','authoritative provider query: no operation')
        self.assertEqual(state['status'], 'PENDING')
        self.assertEqual(state['resolution_evidence'], 'authoritative provider query: no operation')

    def test_event_restart_marks_inflight_unknown(self):
        bus = DurableEventBus(self.db)
        event = Event.create('work', {}, event_id='crash-event')
        bus.publish(event)
        with bus._db.connection() as c:
            c.execute("""INSERT OR REPLACE INTO prain_event_deliveries
                (event_type,consumer_id,event_id,status,attempts,updated_at)
                VALUES(?,?,?,'IN_FLIGHT',1,'now')""", ('work','worker','crash-event'))
        restarted = DurableEventBus(self.db)
        self.assertEqual(restarted.delivery_status('work','worker','crash-event')['status'], 'OUTCOME_UNKNOWN')

    def test_concurrent_duplicate_publish_invokes_handler_once(self):
        import threading
        from concurrent.futures import ThreadPoolExecutor

        bus = DurableEventBus(self.db)
        entered = threading.Event()
        release = threading.Event()
        calls = []
        def handler(event):
            calls.append(event.event_id)
            entered.set()
            if not release.wait(timeout=3):
                raise TimeoutError("test handler release timed out")

        bus.subscribe("race", "worker", handler)
        event = Event.create("race", {}, event_id="race-event")
        with ThreadPoolExecutor(max_workers=8) as pool:
            first = pool.submit(bus.publish, event)
            self.assertTrue(entered.wait(timeout=2))
            others = [pool.submit(bus.publish, event) for _ in range(7)]
            results = [future.result(timeout=2) for future in others]
            self.assertTrue(all(result["worker"] in {"in_flight", "duplicate_ignored"} for result in results))
            release.set()
            self.assertEqual(first.result(timeout=3)["worker"], "processed")
        self.assertEqual(calls, ["race-event"])
        self.assertEqual(bus.delivery_status("race", "worker", "race-event")["status"], "SUCCEEDED")

    def test_reconciled_not_executed_delivery_resumes_on_subscription(self):
        bus = DurableEventBus(self.db)
        event = Event.create("recover", {"job": 1}, event_id="recover-event")
        bus.subscribe("recover", "worker", lambda e: (_ for _ in ()).throw(TimeoutError("provider timeout")))
        with self.assertRaises(TimeoutError):
            bus.publish(event)
        state = bus.reconcile_delivery(
            "recover", "worker", event.event_id, "NOT_EXECUTED",
            "provider lookup confirmed no operation was created"
        )
        self.assertEqual(state["status"], "PENDING")

        calls = []
        restarted = DurableEventBus(self.db)
        restarted.subscribe("recover", "worker", lambda e: calls.append(e.event_id))
        self.assertEqual(calls, ["recover-event"])
        self.assertEqual(restarted.delivery_status("recover", "worker", event.event_id)["status"], "SUCCEEDED")

    def test_reconciliation_rejects_non_unknown_delivery(self):
        bus = DurableEventBus(self.db)
        bus.subscribe("stable", "worker", lambda event: None)
        event = Event.create("stable", {}, event_id="stable-event")
        self.assertEqual(bus.publish(event)["worker"], "processed")
        with self.assertRaisesRegex(ValueError, "delivery_not_outcome_unknown"):
            bus.reconcile_delivery("stable", "worker", event.event_id, "NOT_EXECUTED", "evidence")

    def test_evidence_chain_persists_and_verifies(self):
        ledger=DurableEvidenceLedger(self.db)
        first=ledger.append('test','subject',{'n':1})
        ledger.append('test','subject',{'n':2})
        restarted=DurableEvidenceLedger(self.db)
        self.assertTrue(restarted.verify())
        self.assertEqual(len(restarted.entries()),2)
        self.assertEqual(restarted.entries()[0].entry_hash,first.entry_hash)

    def test_runtime_state_store_persists_across_restart(self):
        runtime=PRAINRuntime(persistent_db_path=self.db)
        first=runtime.state.create('agent/context', {'mode':'observe','counter':1})
        updated=runtime.state.compare_and_swap('agent/context', first.version, {'mode':'reason','counter':2})
        self.assertEqual(updated.version, 2)

        restarted=PRAINRuntime(persistent_db_path=self.db)
        record=restarted.state.get('agent/context')
        self.assertEqual(record.value, {'mode':'reason','counter':2})
        self.assertEqual(record.version, 2)
        self.assertEqual(restarted.snapshot()['state_records'], 1)

    def test_runtime_state_store_rejects_stale_cas_after_restart(self):
        from prain import StateConflict
        first_runtime=PRAINRuntime(persistent_db_path=self.db)
        first_runtime.state.create('shared/key', {'writer':'first'})
        first_runtime.state.compare_and_swap('shared/key', 1, {'writer':'second'})

        restarted=PRAINRuntime(persistent_db_path=self.db)
        with self.assertRaises(StateConflict):
            restarted.state.compare_and_swap('shared/key', 1, {'writer':'stale'})
        self.assertEqual(restarted.state.get('shared/key').value, {'writer':'second'})

    def test_runtime_enables_durable_goals_events_and_evidence(self):
        runtime=PRAINRuntime(persistent_db_path=self.db)
        runtime.goals.create('runtime goal',[{'id':'c','check':'true'}],'runtime-g')
        runtime.ingest(Observation.create('test','heartbeat',{},'obs-persist'))
        self.assertTrue(runtime.evidence.verify())
        restarted=PRAINRuntime(persistent_db_path=self.db)
        self.assertEqual(restarted.goals.get('runtime-g').title,'runtime goal')
        self.assertTrue(restarted.evidence.verify())
        self.assertGreaterEqual(len(restarted.evidence.entries()),1)

if __name__ == '__main__': unittest.main()
