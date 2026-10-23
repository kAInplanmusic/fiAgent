import unittest
from prain.semantic_router import Backend, RouteContext, route


class SemanticRouterTests(unittest.TestCase):
    def setUp(self):
        self.context = RouteContext('tenant-a', 'confidential', frozenset({'eu'}),
                                    frozenset({'local', 'cloud'}), 0.1, 'policy-v1')
        self.local = Backend('local', 'local', 'eu', frozenset({'confidential'}),
                             frozenset({'code'}), .02, .7, external=False)
        self.cloud = Backend('cloud', 'cloud', 'eu', frozenset({'confidential'}),
                             frozenset({'code'}), .01, .99, external=True)

    def test_confidential_never_routes_external(self):
        decision = route('code', self.context, [self.cloud, self.local])
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.backend, 'local')

    def test_no_eligible_backend_denies(self):
        decision = route('code', self.context, [self.cloud])
        self.assertFalse(decision.allowed)
        self.assertIsNone(decision.backend)

    def test_budget_is_hard_constraint(self):
        ctx = RouteContext('t', 'public', frozenset({'eu'}), frozenset({'local'}), .001, 'v1')
        self.assertFalse(route('code', ctx, [self.local]).allowed)

    def test_provider_region_and_capability_are_hard_constraints(self):
        ctx = RouteContext('t', 'public', frozenset({'us'}), frozenset({'local'}), 1, 'v1')
        self.assertFalse(route('code', ctx, [self.local]).allowed)
        ctx = RouteContext('t', 'confidential', frozenset({'eu'}), frozenset({'local'}), 1, 'v1')
        self.assertFalse(route('math', ctx, [self.local]).allowed)

    def test_invalid_security_context_fails_closed(self):
        ctx = RouteContext('', 'confidential', frozenset({'eu'}), frozenset({'local'}), 1, 'v1')
        self.assertEqual(route('code', ctx, [self.local]).reason, 'invalid_security_context')

    def test_quality_ranking_with_deterministic_tie_break(self):
        other = Backend('aaa', 'local', 'eu', frozenset({'confidential'}),
                        frozenset({'code'}), .01, .7, external=False)
        self.assertEqual(route('code', self.context, [self.local, other]).backend, 'aaa')
