import unittest
from datetime import datetime, timezone, timedelta

from prain.anima_hal import Anima, AnimaConflict, HAL, HealthObservation


class AnimaHALContractTests(unittest.TestCase):
    def test_anima_versioned_continuity_and_detachment(self):
        a = Anima("system-1")
        original = {"nested": {"value": 1}}
        m = a.update(expected_version=0, dimension="reason", state=original, provenance="test")
        original["nested"]["value"] = 9
        m.dimensions["reason"]["nested"]["value"] = 8
        self.assertEqual(a.snapshot().dimensions["reason"]["nested"]["value"], 1)
        self.assertEqual(a.snapshot().identity_id, "system-1")
        self.assertEqual(a.snapshot().version, 1)

    def test_anima_stale_cas_rejected(self):
        a = Anima("system-1")
        a.update(expected_version=0, dimension="perception", state={"ok": True}, provenance="observation")
        with self.assertRaisesRegex(AnimaConflict, "stale"):
            a.update(expected_version=0, dimension="reason", state={}, provenance="reason")

    def test_anima_never_grants_authority(self):
        a = Anima("system-1")
        for field in ("grant", "capabilities", "approval", "policy_override"):
            with self.subTest(field=field):
                with self.assertRaises(AnimaConflict):
                    a.update(expected_version=0, dimension="nerve", state={field: ["allow"]}, provenance="test")
        self.assertEqual(a.snapshot().version, 0)

    def test_anima_invalid_dimensions(self):
        a = Anima("system-1")
        with self.assertRaises(ValueError):
            a.update(expected_version=0, dimension="unknown", state={}, provenance="test")

    def test_nested_self_model_cannot_encode_authority(self):
        a = Anima("system-1")
        for state in ({"plan": [{"approval": "allow"}]},
                      {"meta": {"POLICY_OVERRIDE": True}},
                      {"nested": ({"capabilities": ["admin"]},)}):
            with self.subTest(state=state), self.assertRaisesRegex(AnimaConflict, "authority"):
                a.update(expected_version=0, dimension="reason", state=state, provenance="test")
        self.assertEqual(a.snapshot().version, 0)

    def test_hal_observe_only_and_unknown_on_stale(self):
        hal = HAL(max_age_seconds=30)
        now = datetime(2026, 10, 24, 20, 0, tzinfo=timezone.utc)
        recent = (now - timedelta(seconds=10)).isoformat()
        stale = (now - timedelta(seconds=31)).isoformat()
        healthy = hal.assess(HealthObservation("scf", True, recent, "ev"), now)
        self.assertEqual((healthy.health, healthy.action), ("healthy", "observe_only"))
        self.assertEqual(hal.assess(HealthObservation("scf", True, stale, "ev"), now).health, "unknown")
        self.assertEqual(hal.assess(HealthObservation("scf", True, recent, ""), now).health, "unknown")
        self.assertEqual(hal.assess(HealthObservation("scf", False, recent, "ev"), now).health, "unhealthy")
        self.assertEqual(len(hal.history()), 4)

    def test_hal_rejects_non_boolean_and_naive_timestamp(self):
        hal = HAL()
        now = datetime(2026, 10, 24, tzinfo=timezone.utc)
        with self.assertRaises(ValueError):
            hal.assess(HealthObservation("scf", 1, now.isoformat(), "ev"), now)
        with self.assertRaises(ValueError):
            hal.assess(HealthObservation("scf", True, "2026-10-24T00:00:00", "ev"), now)

    def test_hal_never_executes_repair(self):
        hal = HAL()
        now = datetime(2026, 10, 24, tzinfo=timezone.utc)
        result = hal.assess(HealthObservation("scf", False, now.isoformat(), "failure"), now)
        self.assertEqual(result.action, "observe_only")
        self.assertFalse(hasattr(hal, "execute"))
