import sqlite3
import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch
from contextlib import contextmanager
from pathlib import Path

from prain.backup_bundle import backup_databases, restore_databases, recover_database_from_artifact


@contextmanager
def db_connection(path):
    conn = sqlite3.connect(path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def make_db(path, table, key, value):
    with db_connection(path) as conn:
        conn.execute(f"CREATE TABLE {table} (k TEXT PRIMARY KEY, v TEXT NOT NULL)")
        conn.execute(f"INSERT INTO {table}(k,v) VALUES (?,?)", (key, value))


class BackupBundleTests(unittest.TestCase):
    def test_unchecked_bundle_wal_is_rejected_before_destination_changes(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source, target = base / 'source.db', base / 'target.db'
            make_db(source, 'records', 'one', 'backup')
            make_db(target, 'records', 'one', 'keep')
            bundle = base / 'bundle'
            backup_databases({'records': source}, bundle)
            payload = bundle / 'records.sqlite'
            conn = sqlite3.connect(payload)
            self.addCleanup(conn.close)
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA wal_autocheckpoint=0')
            main_hash = hashlib.sha256(payload.read_bytes()).hexdigest()
            manifest_file = bundle / 'BUNDLE_MANIFEST.json'
            manifest = json.loads(manifest_file.read_text())
            manifest['databases']['records']['sha256'] = main_hash
            manifest_file.write_text(json.dumps(manifest))
            conn.execute("UPDATE records SET v='unchecked-wal'")
            conn.commit()
            self.assertEqual(hashlib.sha256(payload.read_bytes()).hexdigest(), main_hash)
            self.assertTrue(Path(str(payload) + '-wal').exists())
            before = target.read_bytes()
            with self.assertRaisesRegex(ValueError, 'sqlite_sidecar_present'):
                restore_databases(bundle, {'records': target})
            self.assertEqual(target.read_bytes(), before)

    def test_live_destination_wal_is_rejected_without_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source, target = base / 'source.db', base / 'target.db'
            make_db(source, 'records', 'one', 'backup')
            make_db(target, 'records', 'one', 'keep')
            bundle = base / 'bundle'
            backup_databases({'records': source}, bundle)
            conn = sqlite3.connect(target)
            self.addCleanup(conn.close)
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA wal_autocheckpoint=0')
            conn.execute("UPDATE records SET v='live-wal'")
            conn.commit()
            with self.assertRaisesRegex(ValueError, 'sqlite_sidecar_present'):
                restore_databases(bundle, {'records': target})
            self.assertEqual(conn.execute('SELECT v FROM records').fetchone()[0], 'live-wal')

    def test_recovery_rejects_artifact_wal_without_overwriting_destination(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            artifact, target = base / 'artifact.db', base / 'target.db'
            make_db(artifact, 'records', 'one', 'artifact')
            make_db(target, 'records', 'one', 'keep')
            conn = sqlite3.connect(artifact)
            self.addCleanup(conn.close)
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA wal_autocheckpoint=0')
            conn.execute("UPDATE records SET v='unchecked-wal'")
            conn.commit()
            before = target.read_bytes()
            with self.assertRaisesRegex(ValueError, 'sqlite_sidecar_present'):
                recover_database_from_artifact(artifact, target)
            self.assertEqual(target.read_bytes(), before)

    def test_multi_database_backup_restore_round_trip(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            state, admission = base / "state.db", base / "admission.db"
            make_db(state, "state", "s1", "state-value")
            make_db(admission, "admission", "a1", "admission-value")
            bundle = base / "bundle"
            result = backup_databases({"state": state, "admission": admission}, bundle)
            self.assertEqual(result["databases"], 2)
            with db_connection(state) as c: c.execute("UPDATE state SET v='changed'")
            with db_connection(admission) as c: c.execute("UPDATE admission SET v='changed'")
            restore_databases(bundle, {"state": state, "admission": admission})
            with db_connection(state) as c:
                self.assertEqual(c.execute("SELECT v FROM state WHERE k='s1'").fetchone()[0], "state-value")
            with db_connection(admission) as c:
                self.assertEqual(c.execute("SELECT v FROM admission WHERE k='a1'").fetchone()[0], "admission-value")

    def test_tampered_bundle_rejected_before_any_destination_changes(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source, target = base / "source.db", base / "target.db"
            make_db(source, "records", "one", "backup")
            make_db(target, "records", "one", "keep")
            bundle = base / "bundle"
            backup_databases({"records": source}, bundle)
            with db_connection(bundle / "records.sqlite") as c:
                c.execute("UPDATE records SET v='tampered'")
            with self.assertRaisesRegex(ValueError, "bundle_checksum_mismatch"):
                restore_databases(bundle, {"records": target})
            with db_connection(target) as c:
                self.assertEqual(c.execute("SELECT v FROM records WHERE k='one'").fetchone()[0], "keep")

    def test_restore_requires_exact_database_set(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source = base / "source.db"
            make_db(source, "records", "one", "backup")
            bundle = base / "bundle"
            backup_databases({"records": source}, bundle)
            with self.assertRaisesRegex(ValueError, "destination_names_must_match_bundle"):
                restore_databases(bundle, {"other": base / "other.db"})

    def test_failed_second_replace_rolls_back_first_destination(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source_a, source_b = base / "source-a.db", base / "source-b.db"
            target_a, target_b = base / "target-a.db", base / "target-b.db"
            make_db(source_a, "records", "one", "new-a")
            make_db(source_b, "records", "one", "new-b")
            make_db(target_a, "records", "one", "old-a")
            make_db(target_b, "records", "one", "old-b")
            bundle = base / "bundle"
            backup_databases({"a": source_a, "b": source_b}, bundle)

            real_replace = __import__("os").replace
            calls = 0
            def fail_second_staged_replace(src, dst):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected second replacement failure")
                return real_replace(src, dst)

            with patch("prain.backup_bundle.os.replace", side_effect=fail_second_staged_replace):
                with self.assertRaisesRegex(OSError, "injected second replacement failure"):
                    restore_databases(bundle, {"a": target_a, "b": target_b})
            with db_connection(target_a) as c:
                self.assertEqual(c.execute("SELECT v FROM records WHERE k='one'").fetchone()[0], "old-a")
            with db_connection(target_b) as c:
                self.assertEqual(c.execute("SELECT v FROM records WHERE k='one'").fetchone()[0], "old-b")

    def test_failed_rollback_preserves_recovery_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source_a, source_b = base / "source-a.db", base / "source-b.db"
            target_a, target_b = base / "target-a.db", base / "target-b.db"
            make_db(source_a, "records", "one", "new-a")
            make_db(source_b, "records", "one", "new-b")
            make_db(target_a, "records", "one", "old-a")
            make_db(target_b, "records", "one", "old-b")
            bundle = base / "bundle"
            backup_databases({"a": source_a, "b": source_b}, bundle)

            real_replace = __import__("os").replace
            calls = 0
            def fail_replace_and_rollback(src, dst):
                nonlocal calls
                calls += 1
                if calls in (2, 3):
                    raise OSError(f"injected replacement failure {calls}")
                return real_replace(src, dst)

            with patch("prain.backup_bundle.os.replace", side_effect=fail_replace_and_rollback):
                with self.assertRaisesRegex(RuntimeError, "restore_failed_and_rollback_incomplete"):
                    restore_databases(bundle, {"a": target_a, "b": target_b})
            recovery_files = list(base.glob(".target-a.db.rollback-*.sqlite"))
            self.assertEqual(len(recovery_files), 1, "failed rollback must retain original database copy")
            with db_connection(recovery_files[0]) as c:
                self.assertEqual(c.execute("SELECT v FROM records WHERE k='one'").fetchone()[0], "old-a")

    def test_recovery_artifact_restores_target_and_is_retained(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            artifact, target = base / "recovery.sqlite", base / "target.sqlite"
            make_db(artifact, "records", "one", "original")
            make_db(target, "records", "one", "damaged-state")
            result = recover_database_from_artifact(artifact, target)
            self.assertEqual(result["status"], "RECOVERED")
            self.assertTrue(result["artifact_retained"])
            self.assertTrue(artifact.exists())
            with db_connection(target) as conn:
                self.assertEqual(conn.execute("SELECT v FROM records WHERE k='one'").fetchone()[0], "original")

    def test_invalid_recovery_artifact_does_not_replace_target(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            artifact, target = base / "bad.sqlite", base / "target.sqlite"
            artifact.write_bytes(b"not a sqlite database")
            make_db(target, "records", "one", "keep")
            with self.assertRaises(sqlite3.DatabaseError):
                recover_database_from_artifact(artifact, target)
            with db_connection(target) as conn:
                self.assertEqual(conn.execute("SELECT v FROM records WHERE k='one'").fetchone()[0], "keep")

    def test_restore_rejects_destination_inside_bundle(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source = base / "source.db"
            make_db(source, "records", "one", "backup")
            bundle = base / "bundle"
            backup_databases({"records": source}, bundle)
            with self.assertRaisesRegex(ValueError, "destination_must_not_overwrite_bundle_contents"):
                restore_databases(bundle, {"records": bundle / "records.sqlite"})

    def test_backup_refuses_existing_bundle_and_duplicate_sources(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source = base / "source.db"
            make_db(source, "records", "one", "backup")
            bundle = base / "bundle"
            backup_databases({"records": source}, bundle)
            with self.assertRaises(FileExistsError):
                backup_databases({"records": source}, bundle)
            with self.assertRaisesRegex(ValueError, "database_paths_must_be_unique"):
                backup_databases({"one": source, "two": source}, base / "other-bundle")


    def test_wal_database_snapshot_and_restore_preserves_committed_rows(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source, target = root / "source.db", root / "target.db"
            with db_connection(source) as conn:
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("CREATE TABLE records (k TEXT PRIMARY KEY, v TEXT NOT NULL)")
                conn.execute("INSERT INTO records VALUES ('one', 'committed')")
            make_db(target, "records", "one", "old")
            bundle = root / "bundle"
            backup_databases({"records": source}, bundle)
            restore_databases(bundle, {"records": target})
            with db_connection(target) as conn:
                self.assertEqual(conn.execute("SELECT v FROM records WHERE k='one'").fetchone()[0], "committed")

    def test_rollback_snapshot_is_valid_sqlite_database(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source, target = root / "source.db", root / "target.db"
            make_db(source, "records", "one", "new")
            make_db(target, "records", "one", "old")
            bundle = root / "bundle"
            backup_databases({"records": source}, bundle)
            real_replace = __import__("os").replace
            def fail_restore(src, dst):
                if Path(dst) == target and ".restore-" in Path(src).name:
                    raise OSError("injected replacement failure")
                return real_replace(src, dst)
            with patch("prain.backup_bundle.os.replace", side_effect=fail_restore):
                with self.assertRaisesRegex(OSError, "injected replacement failure"):
                    restore_databases(bundle, {"records": target})
            with db_connection(target) as conn:
                self.assertEqual(conn.execute("SELECT v FROM records WHERE k='one'").fetchone()[0], "old")


if __name__ == "__main__":
    unittest.main()

