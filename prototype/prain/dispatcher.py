"""Conservative durable outbox dispatcher; external handlers must be explicitly injected.

No handler is configured by default. Exceptions are treated as ambiguous outcomes, never
as proof that the operation did not happen. OUTCOME_UNKNOWN is never automatically retried.
"""
from __future__ import annotations
from typing import Any, Callable
from .durable_admission import AdmissionConflict, DurableAdmissionStore

Handler = Callable[[dict[str, Any], str], str]

class OutboxDispatcher:
    """Dispatch one claimed item through an explicit handler.

    Handler receives (payload, idempotency_key) and must return SUCCEEDED or FAILED.
    A handler may return OUTCOME_UNKNOWN when its provider result is ambiguous.
    Exceptions are persisted as OUTCOME_UNKNOWN. No handler means no claim or execution.
    """
    def __init__(self, store: DurableAdmissionStore, handler: Handler | None = None):
        self.store = store
        self.handler = handler

    def run_once(self) -> dict[str, Any] | None:
        if self.handler is None:
            return None
        item = self.store.claim_next()
        if item is None:
            return None
        try:
            status = self.handler(item['payload'], item['idempotency_key'])
            if status not in {'SUCCEEDED', 'FAILED', 'OUTCOME_UNKNOWN'}:
                raise ValueError('handler must return SUCCEEDED, FAILED, or OUTCOME_UNKNOWN')
            error = 'handler_reported_ambiguous_outcome' if status == 'OUTCOME_UNKNOWN' else None
        except Exception as exc:  # ambiguity: external operation may already have happened
            status = 'OUTCOME_UNKNOWN'
            error = f'handler_exception:{type(exc).__name__}:{str(exc)[:300]}'
        self.store.record_outcome(item['outbox_id'], status, error)
        item['status'] = status
        item['last_error'] = error
        return item

    def reconcile(self, idempotency_key: str, provider_state: str, evidence: str) -> dict[str, Any]:
        """Apply an authoritative reconciliation result to an OUTCOME_UNKNOWN item.

        provider_state is SUCCEEDED, FAILED, or NOT_EXECUTED. NOT_EXECUTED safely returns
        the row to PENDING; callers must only use it when trusted evidence proves no effect.
        """
        if provider_state not in {'SUCCEEDED', 'FAILED', 'NOT_EXECUTED'}:
            raise ValueError('provider_state must be SUCCEEDED, FAILED, or NOT_EXECUTED')
        if not isinstance(evidence, str) or not evidence.strip():
            raise ValueError('reconciliation evidence is required')
        result = self.store.reconcile_unknown(idempotency_key, provider_state, evidence.strip())
        return result
