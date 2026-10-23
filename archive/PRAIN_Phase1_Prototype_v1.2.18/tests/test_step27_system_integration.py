import sqlite3
import tempfile
import unittest
from pathlib import Path
from contextlib import contextmanager

from prain.backup_bundle import backup_databases, restore_databases
from prain.durable_admission import DurableAdmissionStore
from prain.durable_components import DurableGoalRegistry, DurableEventBus, DurableEvidenceLedger
from prain.durable_state_store import DurableStateStore
from prain.event_bus import Event


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


class SystemIntegrationTests(unittest.TestCase):
    def test_persistent_components_survive_restart_and_coordinated_restore(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            paths = {
                "state": base / "state.db",
                "goals": base / "goals.db",
                "events": base / "events.db",
                "evidence": base / "evidence.db",
                "admission": base / "admission.db",
            }

            state = DurableStateStore(paths["state"])
            state.create("system.health", {"status": "healthy", "epoch": 7})
            goals = DurableGoalRegistry(paths["goals"])
            goals.create("Keep state consistent", [{"id": "c1", "check": "state_epoch_matches"}], goal_id="goal-1")
            events = DurableEventBus(paths["events"])
            events.publish(Event.create("prain.integration.checkpoint", {"epoch": 7}, correlation_id="corr-27"))
            evidence = DurableEvidenceLedger(paths["evidence"])
            evidence.append("integration.checkpoint", "corr-27", {"epoch": 7})
            DurableAdmissionStore(paths["admission"])

            bundle = base / "checkpoint"
            backup_databases(paths, bundle)

            # Simulate post-checkpoint drift in every database.
            state.compare_and_swap("system.health", 1, {"status": "drifted", "epoch": 8})
            goals.set_status("goal-1", "active")
            events.publish(Event.create("prain.integration.drift", {"epoch": 8}, correlation_id="corr-27"))
            evidence.append("integration.drift", "corr-27", {"epoch": 8})
            with db_connection(paths["admission"]) as c:
                c.execute("INSERT INTO admission(idempotency_key,fingerprint,receipt_json) VALUES('drift','f','{}')")

            restore_databases(bundle, paths)

            # Reopen each component as a fresh process would; validate durable state and chain.
            restored_state = DurableStateStore(paths["state"])
            self.assertEqual(restored_state.get("system.health").value, {"status": "healthy", "epoch": 7})
            self.assertEqual(DurableGoalRegistry(paths["goals"]).get("goal-1").status, "proposed")
            with db_connection(paths["events"]) as c:
                self.assertEqual(c.execute("SELECT COUNT(*) FROM prain_events").fetchone()[0], 1)
            restored_evidence = DurableEvidenceLedger(paths["evidence"])
            self.assertTrue(restored_evidence.verify())
            self.assertEqual(len(restored_evidence._entries), 1)
            with db_connection(paths["admission"]) as c:
                self.assertEqual(c.execute("SELECT COUNT(*) FROM admission").fetchone()[0], 0)

    def test_restore_rejects_missing_database_before_any_destination_changes(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            src, target = base / "src.db", base / "target.db"
            with db_connection(src) as c:
                c.execute("CREATE TABLE sample(value TEXT)")
                c.execute("INSERT INTO sample VALUES('backup')")
            with db_connection(target) as c:
                c.execute("CREATE TABLE sample(value TEXT)")
                c.execute("INSERT INTO sample VALUES('keep')")
            bundle = base / "bundle"
            backup_databases({"sample": src}, bundle)
            (bundle / "sample.sqlite").unlink()
            with self.assertRaises((FileNotFoundError, ValueError)):
                restore_databases(bundle, {"sample": target})
            with db_connection(target) as c:
                self.assertEqual(c.execute("SELECT value FROM sample").fetchone()[0], "keep")


if __name__ == "__main__":
    unittest.main()
