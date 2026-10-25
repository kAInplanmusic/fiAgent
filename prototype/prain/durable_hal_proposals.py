"""Durable, review-only HAL proposals with restart-safe quota and cooldown.

No repair execution or capability delegation. SQLite serializes admissions.
"""
import sqlite3
import math
from pathlib import Path
from .anima_hal import HALAssessment
from .hal_proposals import RepairProposal


class DurableHALProposalController:
    def __init__(self, database, cooldown_seconds=60, max_proposals=3):
        if type(cooldown_seconds) not in (int, float) or not math.isfinite(cooldown_seconds) or cooldown_seconds <= 0:
            raise ValueError("invalid_cooldown")
        if type(max_proposals) is not int or max_proposals < 1:
            raise ValueError("invalid_budget")
        self.database = str(database)
        self.cooldown, self.budget = cooldown_seconds, max_proposals
        Path(self.database).parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS prain_hal_proposals(
                proposal_id TEXT PRIMARY KEY, component TEXT NOT NULL,
                issued_at REAL NOT NULL, action TEXT NOT NULL, status TEXT NOT NULL,
                reason TEXT NOT NULL)""")

    def _db(self):
        return sqlite3.connect(self.database, timeout=15)

    def propose(self, assessment, now, proposal_id):
        if not isinstance(assessment, HALAssessment):
            raise ValueError("assessment_required")
        if type(now) not in (int, float) or not math.isfinite(now):
            raise ValueError("invalid_clock")
        if not isinstance(proposal_id, str) or not proposal_id.strip():
            raise ValueError("proposal_id_required")
        if not isinstance(assessment.component, str) or not assessment.component.strip():
            raise ValueError("component_required")
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute("SELECT 1 FROM prain_hal_proposals WHERE proposal_id=?", (proposal_id,)).fetchone()
            if prior:
                raise ValueError("proposal_id_already_used")
            last = db.execute("""SELECT MAX(issued_at) FROM prain_hal_proposals
                                 WHERE component=? AND status='pending_approval'""",
                              (assessment.component,)).fetchone()[0]
            count = db.execute("""SELECT COUNT(*) FROM prain_hal_proposals
                                  WHERE status='pending_approval'""").fetchone()[0]
            if assessment.health != "unhealthy":
                status, reason = "blocked", "health_not_verified_unhealthy"
            elif count >= self.budget:
                status, reason = "blocked", "proposal_budget_exhausted"
            elif last is not None and now - last < self.cooldown:
                status, reason = "blocked", "cooldown"
            else:
                status, reason = "pending_approval", "requires_authorized_review"
            proposal = RepairProposal(assessment.component, proposal_id, "request_repair_review",
                                      status, reason)
            db.execute("INSERT INTO prain_hal_proposals VALUES(?,?,?,?,?,?)",
                      (proposal_id, assessment.component, now, proposal.action, status, reason))
            return proposal

    def history(self):
        with self._db() as db:
            rows = db.execute("""SELECT component,proposal_id,action,status,reason
                                 FROM prain_hal_proposals ORDER BY rowid""").fetchall()
        return [RepairProposal(*row) for row in rows]
