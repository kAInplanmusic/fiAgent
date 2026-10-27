"""No private backup/rollback data is installed before current deletion replay."""
import os
from pathlib import Path
import re
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from prain.backup_bundle import backup_databases, restore_databases, recover_database_from_artifact
from prain.private_projections import PrivateProjections, ProjectionDeleted


class RestorePrivacyBarrierTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.live = self.root / "live.sqlite"
        self.store = PrivateProjections(self.live)
        for tenant in ("a", "b"):
            self.store.upsert(tenant, "subject", "restricted", {"personal": "old"})
        self.bundle = self.root / "old-backup"
        backup_databases({"private": self.live}, self.bundle)

    def assert_deleted(self, path, tenant="a"):
        store = PrivateProjections(path)
        self.assertIsNone(store.read(tenant, "subject"))
        with self.assertRaises(ProjectionDeleted):
            store.upsert(tenant, "subject", "restricted", {"personal": "replayed"})

    def test_missing_or_invalid_snapshot_does_not_modify_destination(self):
        self.store.delete_source("a", "subject")
        before = self.live.read_bytes()
        for snapshots in (None, {}, {"private": None}, {"private": [("a", "subject"), ("invalid",)]},
                          {"other": []}):
            with self.subTest(snapshot=snapshots), self.assertRaises(ValueError):
                restore_databases(self.bundle, {"private": self.live}, authoritative_tombstones=snapshots)
            self.assertEqual(self.live.read_bytes(), before)

    def test_deleted_backup_rows_never_installed_and_other_tenant_retained(self):
        self.store.delete_source("a", "subject")
        replace = os.replace
        observed = []
        def inspect_replace(source, destination):
            if Path(destination) == self.live:
                self.assert_deleted(source)
                observed.append(True)
            return replace(source, destination)
        with patch("prain.backup_bundle.os.replace", side_effect=inspect_replace):
            restore_databases(self.bundle, {"private": self.live},
                              authoritative_tombstones={"private": self.store.deletion_snapshot()})
        self.assertEqual(observed, [True])
        self.assert_deleted(self.live)
        self.assertIsNotNone(PrivateProjections(self.live).read("b", "subject"))

    def test_known_destination_tombstones_survive_empty_control_snapshot(self):
        self.store.delete_source("a", "subject")
        restore_databases(self.bundle, {"private": self.live}, authoritative_tombstones={"private": []})
        self.assert_deleted(self.live)

    def test_restored_file_does_not_retain_deleted_payload_in_free_pages(self):
        marker = "PRAIN_DELETION_SENTINEL_" + "Q" * 2048
        self.store.upsert("a", "subject", "restricted", {"personal": marker})
        bundle = self.root / "sentinel-backup"
        backup_databases({"private": self.live}, bundle)
        self.assertIn(marker.encode(), (bundle / "private.sqlite").read_bytes())
        self.store.delete_source("a", "subject")
        target = self.root / "sanitized.sqlite"
        restore_databases(bundle, {"private": target},
                          authoritative_tombstones={"private": [("a", "subject")]})
        self.assert_deleted(target)
        self.assertNotIn(marker.encode(), target.read_bytes())

    def test_new_destination_requires_authoritative_snapshot(self):
        target = self.root / "replica.sqlite"
        with self.assertRaisesRegex(ValueError, "authoritative_tombstones"):
            restore_databases(self.bundle, {"private": target})
        self.assertFalse(target.exists())
        restore_databases(self.bundle, {"private": target},
                          authoritative_tombstones={"private": [("a", "subject")]})
        self.assert_deleted(target)

    def test_newer_destination_hold_blocks_restore_and_recovery(self):
        # The old bundle predates the active hold on the live destination.
        self.store.set_retention('a', 'subject', expires_at='2025-01-01T00:00:00Z',
                                 policy_ref='policy:hold', hold_until='2099-01-01T00:00:00Z')
        before = self.live.read_bytes()
        for snapshot in ([], [('a', 'subject')]):
            with self.subTest(snapshot=snapshot), self.assertRaisesRegex(ValueError, 'legal_hold'):
                restore_databases(self.bundle, {'private': self.live},
                                  authoritative_tombstones={'private': snapshot})
            self.assertEqual(self.live.read_bytes(), before)
        with self.assertRaisesRegex(ValueError, 'legal_hold'):
            recover_database_from_artifact(self.bundle / 'private.sqlite', self.live,
                                           authoritative_tombstones=[])
        self.assertEqual(self.live.read_bytes(), before)

    def test_source_hold_blocks_conflicting_tombstone_before_installation(self):
        self.store.set_retention('a', 'subject', expires_at='2025-01-01T00:00:00Z',
                                 policy_ref='policy:hold', hold_until='2099-01-01T00:00:00Z')
        held_bundle = self.root / 'held-backup'
        backup_databases({'private': self.live}, held_bundle)
        target = self.root / 'new-target.sqlite'
        with self.assertRaisesRegex(ValueError, 'legal_hold'):
            restore_databases(held_bundle, {'private': target},
                              authoritative_tombstones={'private': [('a', 'subject')]})
        self.assertFalse(target.exists())

    def test_nonprivate_bundle_cannot_erase_existing_tombstones(self):
        source = self.root / "generic.sqlite"
        with sqlite3.connect(source) as db:
            db.execute("CREATE TABLE sample(value TEXT)")
            db.execute("INSERT INTO sample VALUES('generic')")
        bundle = self.root / "generic-backup"
        backup_databases({"private": source}, bundle)
        self.store.delete_source("a", "subject")
        with self.assertRaisesRegex(ValueError, "authoritative_tombstones"):
            restore_databases(bundle, {"private": self.live})
        restore_databases(bundle, {"private": self.live}, authoritative_tombstones={"private": []})
        self.assert_deleted(self.live)

    def test_failed_restore_rolls_back_with_current_deletions_applied(self):
        other = self.root / "other.sqlite"
        other_store = PrivateProjections(other)
        other_store.upsert("a", "subject", "restricted", {"personal": "second"})
        bundle = self.root / "two-databases"
        backup_databases({"private": self.live, "other": other}, bundle)
        replace = os.replace
        snapshots = {"private": [("a", "subject")], "other": []}
        def fail_second(source, destination):
            if Path(destination) == other:
                raise OSError("injected second install failure")
            if Path(destination) == self.live:
                self.assert_deleted(source)  # applies both install and rollback
            return replace(source, destination)
        with patch("prain.backup_bundle.os.replace", side_effect=fail_second), self.assertRaises(OSError):
            restore_databases(bundle, {"private": self.live, "other": other}, authoritative_tombstones=snapshots)
        self.assert_deleted(self.live)
        self.assertIsNotNone(PrivateProjections(other).read("a", "subject"))

    def test_failed_rollback_artifact_is_sanitized_and_recovery_rechecks_snapshot(self):
        other = self.root / "other.sqlite"
        PrivateProjections(other).upsert("b", "subject", "restricted", {"personal": "second"})
        bundle = self.root / "two-databases"
        backup_databases({"private": self.live, "other": other}, bundle)
        replace = os.replace
        calls = 0
        def fail_install_then_rollback(source, destination):
            nonlocal calls
            calls += 1
            if calls > 1:
                raise OSError("injected failure")
            return replace(source, destination)
        with patch("prain.backup_bundle.os.replace", side_effect=fail_install_then_rollback):
            with self.assertRaisesRegex(RuntimeError, "rollback_incomplete") as caught:
                restore_databases(bundle, {"private": self.live, "other": other},
                    authoritative_tombstones={"private": [("a", "subject")], "other": []})
        artifact = Path(re.search(r"recovery_artifact=([^;]+)", str(caught.exception)).group(1))
        self.assert_deleted(artifact)
        # Artifact may be older than the authority by the time an operator recovers.
        with self.assertRaisesRegex(ValueError, "authoritative_tombstones"):
            recover_database_from_artifact(artifact, self.live)
        recover_database_from_artifact(artifact, self.live,
                                      authoritative_tombstones=[("a", "subject"), ("b", "subject")])
        self.assert_deleted(self.live, "a")
        self.assert_deleted(self.live, "b")
        self.assertTrue(artifact.exists())

    def test_artifact_without_snapshot_leaves_target_unchanged(self):
        artifact = self.bundle / "private.sqlite"
        before = self.live.read_bytes()
        with self.assertRaisesRegex(ValueError, "authoritative_tombstones"):
            recover_database_from_artifact(artifact, self.live)
        self.assertEqual(self.live.read_bytes(), before)
