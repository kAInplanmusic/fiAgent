# Step 33 — Policy-constrained deterministic router reference

**Release:** v1.2.18. **Scope:** implemented routing reference only, not authenticated gateway, semantic embeddings, Hamilton, Burr or MMAC.

Added `prain/semantic_router.py`: immutable route context and backend descriptors, explicit denial, strict tenant/context presence, classification, permitted provider and region, capability, budget and local-only confidential routing. Ranking optimizes quality and cost only after hard policy filtering. Added six negative/positive tests.

Security limitations: the caller supplies the context and must authenticate it; no real model invocation, no budget reservation/CAS, no semantic intent inference, no cache, no provider health/failover, no durable route evidence. Not a production security boundary. Phase 1 remains PARTIAL_PASS.
