import multiprocessing
import tempfile
import unittest
from pathlib import Path
from prain.durable_state_store import DurableStateStore
from prain.state_store import StateConflict

def _cas_worker(db_path, ready, results):
    store = DurableStateStore(db_path)
    ready.wait()
    try:
        store.compare_and_swap('shared', 1, {'writer': multiprocessing.current_process().name})
        results.put('won')
    except StateConflict:
        results.put('conflict')

class DurableStateStoreTests(unittest.TestCase):
    def test_state_survives_reopen_and_preserves_version(self):
        with tempfile.TemporaryDirectory() as td:
            path = str(Path(td) / 'state.sqlite')
            first = DurableStateStore(path)
            first.create('agent/context', {'nested': [1, 2]})
            first.compare_and_swap('agent/context', 1, {'nested': [1, 2, 3]})
            reopened = DurableStateStore(path).get('agent/context')
            self.assertEqual(reopened.value, {'nested': [1, 2, 3]})
            self.assertEqual(reopened.version, 2)

    def test_stale_cas_is_rejected_after_restart(self):
        with tempfile.TemporaryDirectory() as td:
            path = str(Path(td) / 'state.sqlite')
            DurableStateStore(path).create('k', 1)
            DurableStateStore(path).compare_and_swap('k', 1, 2)
            with self.assertRaises(StateConflict):
                DurableStateStore(path).compare_and_swap('k', 1, 3)

    def test_duplicate_create_rejected_across_instances(self):
        with tempfile.TemporaryDirectory() as td:
            path = str(Path(td) / 'state.sqlite')
            DurableStateStore(path).create('k', 1)
            with self.assertRaises(StateConflict):
                DurableStateStore(path).create('k', 2)

    def test_multi_process_cas_allows_exactly_one_winner(self):
        with tempfile.TemporaryDirectory() as td:
            path = str(Path(td) / 'state.sqlite')
            DurableStateStore(path).create('shared', {'writer': 'initial'})
            ctx = multiprocessing.get_context('spawn')
            ready = ctx.Event(); results = ctx.Queue()
            workers = [ctx.Process(target=_cas_worker, args=(path, ready, results), name=f'writer-{i}') for i in range(4)]
            for worker in workers: worker.start()
            ready.set()
            outcomes = [results.get(timeout=15) for _ in workers]
            for worker in workers:
                worker.join(15)
                self.assertEqual(worker.exitcode, 0)
            self.assertEqual(outcomes.count('won'), 1)
            self.assertEqual(outcomes.count('conflict'), 3)
            self.assertEqual(DurableStateStore(path).get('shared').version, 2)

if __name__ == '__main__': unittest.main()
