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

    def test_evidence_chain_persists_and_verifies(self):
        ledger=DurableEvidenceLedger(self.db)
        first=ledger.append('test','subject',{'n':1})
        ledger.append('test','subject',{'n':2})
        restarted=DurableEvidenceLedger(self.db)
        self.assertTrue(restarted.verify())
        self.assertEqual(len(restarted.entries()),2)
        self.assertEqual(restarted.entries()[0].entry_hash,first.entry_hash)

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
