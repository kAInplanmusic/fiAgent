import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from prain.anima_hal import Anima, AnimaConflict
from prain.durable_semantics import DurableAnima, _contains_authority_field


class DurableAnimaAuthorityTests(unittest.TestCase):
    def test_in_memory_mutation_after_snapshot_does_not_grant_authority(self):
        model = Anima('identity')
        external = {'nested': {'label': 'safe'}}

        def mutate_original_and_check(snapshot):
            external['nested']['grant'] = 'admin'
            return 'grant' in snapshot['nested']

        with patch('prain.anima_hal._contains_authority_field', side_effect=mutate_original_and_check):
            model.update(expected_version=0, dimension='anima', state=external, provenance='test')
        self.assertEqual(model.snapshot().dimensions['anima'], {'nested': {'label': 'safe'}})

    def test_nested_authority_is_rejected_without_writing(self):
        with tempfile.TemporaryDirectory() as root:
            db = str(Path(root) / 'state.sqlite')
            model = DurableAnima('identity', db)
            for state in ({'nested': [{'CAPABILITIES': ['admin']}]},
                          {'nested': {'policy_override': True}},
                          {'nested': [{'approval': {'grant': 'admin'}}]}):
                with self.subTest(state=state), self.assertRaisesRegex(AnimaConflict, 'authority'):
                    model.update(expected_version=0, dimension='anima', state=state, provenance='test')
                self.assertEqual(DurableAnima('identity', db).snapshot().version, 0)
            updated = model.update(expected_version=0, dimension='anima',
                                   state={'nested': [{'label': 'safe'}]}, provenance='test')
            self.assertEqual(updated.version, 1)
            self.assertEqual(DurableAnima('identity', db).snapshot().dimensions['anima'],
                             {'nested': [{'label': 'safe'}]})

    def test_mutation_after_snapshot_does_not_enter_persisted_model(self):
        with tempfile.TemporaryDirectory() as root:
            db = str(Path(root) / 'state.sqlite')
            model = DurableAnima('identity', db)
            external = {'nested': {'label': 'safe'}}

            def mutate_original_and_check(snapshot):
                external['nested']['grant'] = 'admin'
                return _contains_authority_field(snapshot)

            with patch('prain.durable_semantics._contains_authority_field', side_effect=mutate_original_and_check):
                model.update(expected_version=0, dimension='anima', state=external, provenance='test')
            self.assertEqual(DurableAnima('identity', db).snapshot().dimensions['anima'],
                             {'nested': {'label': 'safe'}})


if __name__ == '__main__':
    unittest.main()
