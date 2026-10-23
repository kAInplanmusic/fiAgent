import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from prain.goal_registry import GoalRegistry, GoalError
from prain.durable_components import DurableGoalRegistry, DurableEvidenceLedger
from prain.evidence_ledger import EvidenceLedger
from prain.semantic_router import Backend, RouteContext, route
from prain.policy_gateway import PolicyGateway, ActionRequest, _canonical_hash


class GoalVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.registries = [GoalRegistry(), DurableGoalRegistry(Path(self.temp.name) / 'goals.db')]

    def create(self, registry, count=1):
        goal = registry.create('goal', [{'id': str(i), 'check': 'check'} for i in range(count)])
        registry.activate(goal.goal_id)
        return goal.goal_id

    def test_truthy_non_booleans_cannot_complete(self):
        for registry in self.registries:
            gid = self.create(registry)
            for value in ['false', 1, 0, None, [], {}]:
                with self.subTest(adapter=type(registry).__name__, value=value):
                    with self.assertRaises(GoalError):
                        registry.record_verification(gid, value, ['e1'], 'verifier')
                    self.assertEqual(registry.get(gid).status, 'active')

    def test_empty_or_malformed_evidence_rejected(self):
        for registry in self.registries:
            gid = self.create(registry)
            for refs in [[], [''], [' '], [None], 'evidence', None]:
                with self.assertRaises(GoalError):
                    registry.record_verification(gid, True, refs, 'verifier')

    def test_every_criterion_requires_its_own_result(self):
        for registry in self.registries:
            gid = self.create(registry, 2)
            with self.assertRaises(GoalError):
                registry.record_verification(gid, True, ['e1'], 'verifier')
            good = [{'id': str(i), 'passed': True, 'evidence_refs': [f'e{i}']} for i in range(2)]
            for bad in [good[:1], good + [good[0]], [good[0], {'id':'1', 'passed':False, 'evidence_refs':[]}]]:
                with self.assertRaises(GoalError):
                    registry.record_verification(gid, True, ['e1'], 'verifier', bad)
            done = registry.record_verification(gid, True, ['e0', 'e1'], 'verifier', good)
            self.assertEqual(done.status, 'completed')
            self.assertEqual(len(done.verification['criterion_results']), 2)
            with self.assertRaises(GoalError):
                registry.set_status(gid, 'active')

    def test_criteria_are_unique_and_detached(self):
        for registry in self.registries:
            criteria = [{'id':'c', 'check':'original'}]
            goal = registry.create('goal', criteria)
            criteria[0]['check'] = 'changed'
            self.assertEqual(registry.get(goal.goal_id).acceptance_criteria[0]['check'], 'original')
            with self.assertRaises(GoalError):
                registry.create('goal', criteria * 2)
            with self.assertRaises(GoalError):
                registry.record_verification(goal.goal_id, True, ['e'], 'v')


class EvidenceIntegrityTests(unittest.TestCase):
    def test_returned_payloads_cannot_mutate_chain(self):
        ledger = EvidenceLedger()
        payload = {'nested': {'value': 1}}
        entry = ledger.append('test', 'subject', payload)
        payload['nested']['value'] = 2
        entry.payload['nested']['value'] = 3
        ledger.entries()[0].payload['nested']['value'] = 4
        self.assertTrue(ledger.verify())
        self.assertEqual(ledger.entries()[0].payload['nested']['value'], 1)

    def test_multiple_instances_share_transactional_head(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / 'evidence.db'
            ledgers = [DurableEvidenceLedger(db) for _ in range(4)]
            with ThreadPoolExecutor(max_workers=4) as pool:
                list(pool.map(lambda i: ledgers[i % 4].append('test', 'subject', {'i':i}), range(40)))
            for ledger in ledgers:
                self.assertTrue(ledger.verify())
                self.assertEqual(len(ledger.entries()), 40)
            self.assertTrue(DurableEvidenceLedger(db).verify())

    def test_corrupt_chain_is_not_extended(self):
        with tempfile.TemporaryDirectory() as temp:
            db = Path(temp) / 'evidence.db'
            ledger = DurableEvidenceLedger(db)
            ledger.append('test', 'subject', {'value':1})
            with sqlite3.connect(db) as conn:
                conn.execute("UPDATE prain_evidence SET data_json=replace(data_json, '\"value\":1', '\"value\":2')")
            self.assertFalse(ledger.verify())
            with self.assertRaises(ValueError):
                ledger.append('test', 'subject', {})
            self.assertEqual(len(ledger.entries()), 1)

    def test_invalid_append_does_not_poison_transaction(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger = DurableEvidenceLedger(Path(temp) / 'evidence.db')
            with self.assertRaises(ValueError):
                ledger.append('test', 'subject', {'value':float('nan')})
            ledger.append('test', 'subject', {'value':1})
            self.assertTrue(ledger.verify())
            self.assertEqual(len(ledger.entries()), 1)


class RoutingBoundaryTests(unittest.TestCase):
    def context(self, budget=1):
        return RouteContext('tenant', 'public', frozenset({'eu'}), frozenset({'provider'}), budget, 'v1')

    def backend(self, cost=0.1, quality=0.8):
        return Backend('model', 'provider', 'eu', frozenset({'public'}), frozenset({'task'}), cost, quality)

    def test_invalid_budget_denies(self):
        for value in [float('nan'), float('inf'), float('-inf'), True, '1', None, 10 ** 1000]:
            self.assertFalse(route('task', self.context(value), [self.backend()]).allowed)

    def test_invalid_backend_numbers_are_filtered(self):
        for value in [float('nan'), float('inf'), float('-inf'), True, '1', None, 10 ** 1000]:
            self.assertFalse(route('task', self.context(), [self.backend(cost=value)]).allowed)
            self.assertFalse(route('task', self.context(), [self.backend(quality=value)]).allowed)


class PolicyBoundaryTests(unittest.TestCase):
    def test_naive_expiry_denies_without_exception(self):
        gateway = PolicyGateway([{'policy_id':'p', 'action':'run', 'required_capability':'run', 'approval_required':True}])
        request = ActionRequest.create('run', 'target', 'run', 'actor', {})
        approval = {'action':'run', 'target':'target', 'input_hash':_canonical_hash({}),
                    'idempotency_key':request.idempotency_key, 'expires_at':'2099-01-01T00:00:00'}
        decision = gateway.evaluate(request, approval)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, 'approval_expiry_invalid')

    def test_external_rule_mutation_cannot_change_policy(self):
        rules = [{'policy_id':'p', 'action':'run', 'required_capability':'admin'}]
        gateway = PolicyGateway(rules)
        rules[0]['required_capability'] = 'guest'
        self.assertFalse(gateway.evaluate(ActionRequest.create('run', 'target', 'guest', 'actor', {})).allowed)
