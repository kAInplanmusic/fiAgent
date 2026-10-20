from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any
import uuid

def _now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

class GoalError(ValueError):
    pass

@dataclass
class Goal:
    goal_id: str
    title: str
    acceptance_criteria: list[dict[str, Any]]
    status: str
    created_at: str
    updated_at: str
    verification: dict[str, Any] | None = None

class GoalRegistry:
    STATUSES = {"proposed", "active", "blocked", "completed", "failed"}

    def __init__(self):
        self._goals = {}

    def create(self, title, acceptance_criteria, goal_id=None):
        if not title.strip():
            raise GoalError("title must be non-empty")
        if not acceptance_criteria:
            raise GoalError("at least one machine-checkable acceptance criterion is required")
        for c in acceptance_criteria:
            if not isinstance(c, dict) or not c.get("id") or not c.get("check"):
                raise GoalError("each criterion needs non-empty id and check fields")
        gid = goal_id or str(uuid.uuid4())
        if gid in self._goals:
            raise GoalError(f"goal already exists: {gid}")
        now = _now()
        self._goals[gid] = Goal(gid, title, acceptance_criteria, "proposed", now, now)
        return self.get(gid)

    def activate(self, goal_id):
        goal = self._require(goal_id)
        if goal.status != "proposed":
            raise GoalError(f"cannot activate from {goal.status}")
        goal.status, goal.updated_at = "active", _now()
        return self.get(goal_id)

    def set_status(self, goal_id, status):
        goal = self._require(goal_id)
        if status not in self.STATUSES:
            raise GoalError(f"unknown status: {status}")
        if status == "completed":
            raise GoalError("completed requires passing verification")
        goal.status, goal.updated_at = status, _now()
        return self.get(goal_id)

    def record_verification(self, goal_id, passed, evidence_refs, verifier):
        goal = self._require(goal_id)
        if not verifier or not verifier.strip():
            raise GoalError("verifier must be identified")
        if passed and not evidence_refs:
            raise GoalError("passing verification requires evidence references")
        goal.verification = {
            "passed": bool(passed), "evidence_refs": list(evidence_refs),
            "verifier": verifier, "verified_at": _now()
        }
        goal.status = "completed" if passed else "failed"
        goal.updated_at = _now()
        return self.get(goal_id)

    def get(self, goal_id):
        return Goal(**asdict(self._require(goal_id)))

    def list(self):
        return [self.get(gid) for gid in self._goals]

    def _require(self, goal_id):
        if goal_id not in self._goals:
            raise KeyError(f"unknown goal: {goal_id}")
        return self._goals[goal_id]
