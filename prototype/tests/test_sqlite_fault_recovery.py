import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from prain.durable_state_store import DurableStateStore


class SQLiteFaultRecoveryTests(unittest.TestCase):
    def test_transaction_is_rolled_back_after_process_termination(self):
        with tempfile.TemporaryDirectory() as td:
            db = str(Path(td) / "state.sqlite")
            store = DurableStateStore(db)
            store.create("stable", {"value": 1})
            script = r'''
import os, sqlite3, sys
conn = sqlite3.connect(sys.argv[1], isolation_level=None)
conn.execute("BEGIN IMMEDIATE")
conn.execute("INSERT INTO prain_state(state_key,value_json,version,updated_at) VALUES(?,?,?,?)",
             ("uncommitted", '{"value":2}', 1, "test"))
os._exit(17)
'''
            proc = subprocess.run([sys.executable, "-c", script, db], check=False, timeout=10)
            self.assertEqual(proc.returncode, 17)
            reopened = DurableStateStore(db)
            self.assertIsNone(reopened.get("uncommitted"))
            self.assertEqual(reopened.get("stable").value, {"value": 1})
            self.assertEqual(reopened.health_check()["status"], "OK")

    def test_locked_database_fails_without_partial_write_then_recovers(self):
        with tempfile.TemporaryDirectory() as td:
            db = str(Path(td) / "state.sqlite")
            store = DurableStateStore(db, timeout=0.05)
            lock = sqlite3.connect(db, timeout=0.05, isolation_level=None)
            lock.execute("BEGIN IMMEDIATE")
            try:
                with self.assertRaises(sqlite3.OperationalError):
                    store.create("blocked", {"value": 1})
            finally:
                lock.rollback()
                lock.close()
            self.assertIsNone(store.get("blocked"))
            self.assertEqual(store.health_check()["status"], "OK")
            self.assertEqual(store.create("after-lock", 2).value, 2)

    def test_aborted_write_trigger_leaves_no_partial_record(self):
        with tempfile.TemporaryDirectory() as td:
            db = str(Path(td) / 'state.sqlite')
            store = DurableStateStore(db)
            store.create('stable', {'value': 1})
            conn = sqlite3.connect(db)
            try:
                conn.execute("CREATE TRIGGER reject_blocked BEFORE INSERT ON prain_state WHEN NEW.state_key='blocked' BEGIN SELECT RAISE(ABORT, 'injected write failure'); END")
                conn.commit()
            finally: conn.close()
            with self.assertRaisesRegex(sqlite3.IntegrityError, 'injected write failure'):
                store.create('blocked', {'value': 2})
            self.assertIsNone(store.get('blocked'))
            self.assertEqual(store.get('stable').value, {'value': 1})
            self.assertEqual(store.health_check()['status'], 'OK')

    def test_health_check_reports_missing_schema(self):
        with tempfile.TemporaryDirectory() as td:
            db = str(Path(td) / "empty.sqlite")
            sqlite3.connect(db).close()
            report = DurableStateStore.__new__(DurableStateStore)
            report.db_path = db
            report.timeout = 0.1
            self.assertEqual(report.health_check()["status"], "SCHEMA_MISSING")

    def test_health_check_detects_corrupt_database(self):
        with tempfile.TemporaryDirectory() as td:
            db = str(Path(td) / "corrupt.sqlite")
            Path(db).write_bytes(b"not a sqlite database")
            report = DurableStateStore.__new__(DurableStateStore)
            report.db_path = db
            report.timeout = 0.1
            self.assertEqual(report.health_check()["status"], "ERROR")


if __name__ == "__main__":
    unittest.main()
