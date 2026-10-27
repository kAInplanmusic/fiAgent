"""Owned SQLite projection privacy; not evidence of whole-system erasure."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from prain.private_projections import PrivateProjections, ProjectionDeleted

class ProjectionLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)/'live.db'
        self.store = PrivateProjections(self.path)

    def test_nested_credentials_rejected_without_writing(self):
        for field in ('API-Key', 'access_token', 'clientSecret', 'private-key', 'Password'):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'secret_field'):
                self.store.upsert('t', 's', 'restricted', {'records':[{'nested':{field:'sensitive'}}]})
        self.assertIsNone(self.store.read('t','s'))

    def test_deep_or_cyclic_payload_bounded(self):
        payload = {}; payload['self'] = payload
        with self.assertRaisesRegex(ValueError, 'structure_limit'):
            self.store.upsert('t','s','public',payload)

    def test_classification_cannot_be_silently_lowered(self):
        self.store.upsert('t','s','confidential',{'name':'private'})
        with self.assertRaisesRegex(ValueError,'downgrade'):
            self.store.upsert('t','s','public',{'name':'private'})
        self.assertEqual(self.store.read('t','s')['classification'],'confidential')

    def test_sweep_persists_honors_hold_and_limits_work(self):
        for source in ('one','two','held','unconfigured'):
            self.store.upsert('t',source,'internal',{'x':1})
        for source in ('one','two','held'):
            self.store.set_retention('t',source,expires_at='2025-01-01T00:00:00Z',policy_ref='policy:1',
                hold_until='2099-01-01T00:00:00Z' if source=='held' else None)
        self.store = PrivateProjections(self.path)
        report=self.store.sweep_retention(now='2026-01-01T00:00:00Z',limit=1)
        self.assertEqual(report,{'deleted':1,'unconfigured':1})
        self.assertEqual(self.store.sweep_retention(now='2026-01-01T00:00:00Z')['deleted'],1)
        self.assertIsNotNone(self.store.read('t','held'))
        with self.assertRaisesRegex(ValueError,'legal_hold'):
            self.store.delete_source('t','held')
        with self.assertRaises(ProjectionDeleted):
            self.store.upsert('t','one','internal',{'x':2})

    def test_old_backup_requires_current_tombstones_and_preserves_other_tenant(self):
        for tenant in ('a','b'):
            self.store.upsert(tenant,'s','confidential',{'private':'content'})
        restored_path=Path(self.tmp.name)/'restored.db'
        source=sqlite3.connect(self.path); target=sqlite3.connect(restored_path)
        try: source.backup(target)
        finally: source.close(); target.close()
        self.store.delete_source('a','s')
        replica=PrivateProjections(restored_path)
        self.assertIsNotNone(replica.read('a','s')) # proves backup is actually old
        self.assertEqual(replica.apply_deletions(self.store.deletion_snapshot()),1)
        self.assertIsNone(replica.read('a','s'))
        self.assertIsNotNone(replica.read('b','s'))
        replica=PrivateProjections(restored_path)
        with self.assertRaises(ProjectionDeleted):
            replica.upsert('a','s','confidential',{'private':'replayed'})

    def test_invalid_tombstone_batch_atomic(self):
        self.store.upsert('a','s','public',{})
        with self.assertRaises(ValueError):
            self.store.apply_deletions([('a','s'),('bad',)])
        self.assertIsNotNone(self.store.read('a','s'))
        self.assertEqual(self.store.deletion_snapshot(),[])

    def test_tombstone_batch_preserves_all_entries_when_one_has_active_hold(self):
        for source in ('free', 'held'):
            self.store.upsert('a', source, 'restricted', {'data': source})
        self.store.set_retention('a', 'held', expires_at='2025-01-01T00:00:00Z',
                                 policy_ref='policy:hold', hold_until='2099-01-01T00:00:00Z')
        with self.assertRaisesRegex(ValueError, 'blocked_legal_hold'):
            self.store.apply_deletions([('a', 'free'), ('a', 'held')])
        self.assertIsNotNone(self.store.read('a', 'free'))
        self.assertIsNotNone(self.store.read('a', 'held'))
        self.assertEqual(self.store.deletion_snapshot(), [])

    def test_expired_hold_does_not_block_tombstone(self):
        self.store.upsert('a', 's', 'restricted', {'data': 'old'})
        self.store.set_retention('a', 's', expires_at='2024-01-01T00:00:00Z',
                                 policy_ref='policy:hold', hold_until='2025-01-01T00:00:00Z')
        self.assertEqual(self.store.apply_deletions([('a', 's')]), 1)
        self.assertIsNone(self.store.read('a', 's'))

    def test_retention_update_cannot_silently_remove_or_shorten_active_hold(self):
        self.store.upsert('a', 's', 'restricted', {'data': 'held'})
        original = dict(expires_at='2025-01-01T00:00:00Z', policy_ref='policy:hold',
                        hold_until='2099-01-01T00:00:00Z')
        self.store.set_retention('a', 's', **original)
        for replacement in (None, '2098-01-01T00:00:00Z'):
            with self.subTest(replacement=replacement), self.assertRaisesRegex(ValueError, 'active_legal_hold'):
                self.store.set_retention('a', 's', expires_at='2025-01-01T00:00:00Z',
                                         policy_ref='policy:new', hold_until=replacement)
            with sqlite3.connect(self.path) as db:
                row = db.execute('SELECT policy_ref,hold_until FROM prain_projection_retention WHERE tenant=? AND source=?', ('a', 's')).fetchone()
            self.assertEqual(row[0], 'policy:hold')
            self.assertEqual(row[1], self.store._timestamp(original['hold_until']))
            with self.assertRaisesRegex(ValueError, 'legal_hold'):
                self.store.delete_source('a', 's')
        self.store.set_retention('a', 's', expires_at=original['expires_at'],
                                 policy_ref='policy:extend', hold_until='2100-01-01T00:00:00Z')

    def test_naive_retention_timestamp_rejected(self):
        self.store.upsert('a','s','public',{})
        with self.assertRaisesRegex(ValueError,'timezone'):
            self.store.set_retention('a','s',expires_at='2026-01-01',policy_ref='p')
