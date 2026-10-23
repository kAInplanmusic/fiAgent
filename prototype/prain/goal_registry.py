from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any
import uuid
from copy import deepcopy

def validate_criteria(criteria):
    if not isinstance(criteria, list) or not criteria:
        raise GoalError('at least one acceptance criterion is required')
    ids = set()
    for c in criteria:
        if not isinstance(c, dict) or any(not isinstance(c.get(k), str) or not c[k].strip() for k in ('id', 'check')):
            raise GoalError('each criterion needs non-empty string id and check fields')
        if c['id'] in ids:
            raise GoalError('criterion IDs must be unique')
        ids.add(c['id'])
    return deepcopy(criteria)

def validate_verification(goal, passed, evidence_refs, verifier, criterion_results=None):
    if type(passed) is not bool:
        raise GoalError('passed must be a boolean')
    if goal.status != 'active':
        raise GoalError('verification requires an active goal')
    if not isinstance(verifier, str) or not verifier.strip():
        raise GoalError('verifier must be identified')
    def refs(value, required):
        if not isinstance(value, list) or any(not isinstance(r, str) or not r.strip() for r in value) or (required and not value):
            raise GoalError('evidence references must be a list of non-empty strings')
        return list(value)
    refs(evidence_refs, passed)
    criteria = validate_criteria(goal.acceptance_criteria)
    if criterion_results is None:
        if len(criteria) != 1:
            raise GoalError('multi-criterion goals require individual results')
        criterion_results = [{'id': criteria[0]['id'], 'passed': passed, 'evidence_refs': evidence_refs}]
    if not isinstance(criterion_results, list):
        raise GoalError('criterion results must be a list')
    found = {}
    for result in criterion_results:
        if not isinstance(result, dict) or not isinstance(result.get('id'), str) or result['id'] in found or type(result.get('passed')) is not bool:
            raise GoalError('invalid or duplicate criterion result')
        refs(result.get('evidence_refs'), result['passed'])
        found[result['id']] = deepcopy(result)
    if set(found) != {c['id'] for c in criteria}:
        raise GoalError('results must cover exactly every criterion')
    if passed != all(r['passed'] for r in found.values()):
        raise GoalError('overall result conflicts with individual results')
    return {'passed': passed, 'evidence_refs': list(evidence_refs), 'verifier': verifier,
            'criterion_results': list(found.values()), 'verified_at': _now()}

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
        if not isinstance(title, str) or not title.strip():
            raise GoalError("title must be non-empty")
        acceptance_criteria = validate_criteria(acceptance_criteria)
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
        if goal.status in {'completed', 'failed'}:
            raise GoalError('terminal goals cannot be reopened')
        goal.status, goal.updated_at = status, _now()
        return self.get(goal_id)

    def record_verification(self, goal_id, passed, evidence_refs, verifier, criterion_results=None):
        goal = self._require(goal_id)
        goal.verification = validate_verification(goal, passed, evidence_refs, verifier, criterion_results)
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
