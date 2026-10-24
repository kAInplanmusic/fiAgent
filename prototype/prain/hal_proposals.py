"""HAL cooldown and bounded proposal controller; never executes an action."""
from dataclasses import dataclass
from threading import RLock


@dataclass(frozen=True)
class RepairProposal:
    component: str
    proposal_id: str
    action: str
    status: str
    reason: str


class HALProposalController:
    def __init__(self, cooldown_seconds=60, max_proposals=3):
        if type(cooldown_seconds) not in (int, float) or cooldown_seconds <= 0:
            raise ValueError("invalid_cooldown")
        if type(max_proposals) is not int or max_proposals < 1:
            raise ValueError("invalid_budget")
        self.cooldown = cooldown_seconds
        self.budget = max_proposals
        self._history = []
        self._last = {}
        self._lock = RLock()

    def propose(self, assessment, now, proposal_id):
        import math
        if type(now) not in (int, float) or not math.isfinite(now):
            raise ValueError("invalid_clock")
        if not isinstance(proposal_id, str) or not proposal_id.strip():
            raise ValueError("proposal_id_required")
        from .anima_hal import HALAssessment
        if not isinstance(assessment, HALAssessment):
            raise ValueError("assessment_required")
        with self._lock:
            if assessment.health != "unhealthy":
                status, reason = "blocked", "health_not_verified_unhealthy"
            elif any(p.proposal_id == proposal_id for p in self._history):
                status, reason = "blocked", "duplicate_proposal"
            elif len([p for p in self._history if p.status == "pending_approval"]) >= self.budget:
                status, reason = "blocked", "proposal_budget_exhausted"
            elif assessment.component in self._last and now - self._last[assessment.component] < self.cooldown:
                status, reason = "blocked", "cooldown"
            else:
                status, reason = "pending_approval", "requires_authorized_review"
                self._last[assessment.component] = now
            proposal = RepairProposal(assessment.component, proposal_id, "request_repair_review", status, reason)
            self._history.append(proposal)
            return proposal

    def history(self):
        with self._lock:
            return list(self._history)
