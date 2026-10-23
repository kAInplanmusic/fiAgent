import sqlite3
import tempfile
import unittest
from pathlib import Path

from prain.durable_state_store import DurableStateStore


class BackupRestoreTests(unittest.TestCase):
    def test_online_backup_and_restore_preserve_values_and_versions(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source = DurableStateStore(base / "source.sqlite")
            source.create("alpha", {"value": 1})
            source.compare_and_swap("alpha", 1, {"value": 2})
            source.create("beta", [1, 2, 3])
            backup = base / "backup.sqlite"
            self.assertEqual(source.backup_to(backup)["status"], "OK")

            restored = DurableStateStore.restore_from(backup, base / "restored.sqlite")
            alpha = restored.get("alpha")
            self.assertEqual(alpha.value, {"value": 2})
            self.assertEqual(alpha.version, 2)
            self.assertEqual(restored.get("beta").value, [1, 2, 3])
            self.assertEqual(restored.health_check()["status"], "OK")

    def test_backup_refuses_overwrite_and_same_source(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "state.sqlite"
            store = DurableStateStore(db)
            with self.assertRaisesRegex(ValueError, "backup_destination_must_differ"):
                store.backup_to(db)
            backup = Path(td) / "backup.sqlite"
            store.backup_to(backup)
            with self.assertRaises(FileExistsError):
                store.backup_to(backup)

    def test_restore_rejects_invalid_backup_without_replacing_target(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            bad = base / "bad.sqlite"
            bad.write_bytes(b"not sqlite")
            target = base / "target.sqlite"
            target_store = DurableStateStore(target)
            target_store.create("keep", {"safe": True})
            with self.assertRaises(sqlite3.DatabaseError):
                DurableStateStore.restore_from(bad, target)
            self.assertEqual(DurableStateStore(target).get("keep").value, {"safe": True})

    def test_restore_rejects_database_without_expected_schema(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            empty = base / "empty.sqlite"
            sqlite3.connect(empty).close()
            with self.assertRaisesRegex(sqlite3.DatabaseError, "backup_schema_missing"):
                DurableStateStore.restore_from(empty, base / "target.sqlite")

    def test_restore_rejects_incompatible_schema_without_replacing_target(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            bad = base / "bad-schema.sqlite"
            conn = sqlite3.connect(bad)
            try:
                conn.execute("CREATE TABLE prain_state (wrong_column TEXT)")
                conn.commit()
            finally:
                conn.close()
            target = base / "target.sqlite"
            target_store = DurableStateStore(target)
            target_store.create("keep", {"safe": True})
            with self.assertRaisesRegex(sqlite3.DatabaseError, "backup_schema_incompatible"):
                DurableStateStore.restore_from(bad, target)
            self.assertEqual(DurableStateStore(target).get("keep").value, {"safe": True})

    def test_failed_backup_does_not_leave_destination_file(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            malformed = base / "malformed.sqlite"
            conn = sqlite3.connect(malformed)
            try:
                conn.execute("CREATE TABLE unrelated (id INTEGER)")
                conn.commit()
            finally:
                conn.close()
            store = DurableStateStore.__new__(DurableStateStore)
            store.db_path = str(malformed)
            store.timeout = 1.0
            backup = base / "failed-backup.sqlite"
            with self.assertRaisesRegex(sqlite3.DatabaseError, "backup_schema_missing"):
                store.backup_to(backup)
            self.assertFalse(backup.exists())


if __name__ == "__main__":
    unittest.main()
