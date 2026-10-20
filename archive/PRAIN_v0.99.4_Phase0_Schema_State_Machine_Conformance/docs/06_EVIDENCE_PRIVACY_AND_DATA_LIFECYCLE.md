# 6. Evidence integrity, classification, retention and deletion

## 6.1 Classification labels

- `public`: intentionally public and approved for publication.
- `internal`: non-public operational information with limited organizational exposure.
- `confidential`: personal, business-sensitive or security-relevant information restricted to named roles/purposes.
- `restricted`: secrets, credentials, highly sensitive personal data, key material, or data whose disclosure can create material harm.

Secrets and key material should preferably be held by a dedicated credential/key service, not embedded in prompts, general memory or ordinary evidence payloads. Classification can be raised by ingestion policy; it cannot be lowered without an attributable review decision.

## 6.2 Evidence structure and integrity

Evidence manifests contain source identity, producer, tenant, capture/record times, content digest, classification, retention-policy reference and integrity metadata. Large or sensitive content is stored separately as encrypted content addressed by `content_ref`; the manifest should not duplicate personal/secret payload. For structured JSON hashing, use one named canonicalization profile (RFC 8785 JCS where interoperable); for binary data use exact-byte or explicitly declared media-specific canonicalization. Digest algorithm is included in the record, not guessed from digest length.

Where policy requires signatures, record signer key ID, signature algorithm, signature reference, verification time and key-status view. A hash detects changes relative to a known digest but does not by itself prove who created the payload, that the source was truthful or that evidence is legally admissible.

## 6.3 Signing-key lifecycle

- Keys are generated/stored in an approved KMS/HSM or equivalent secret boundary and scoped by purpose and tenant/authority.
- Public verification material and key status have versioned references; private key material is never written to ordinary event logs, prompts, memory or evidence blobs.
- Rotation creates a new key version and records activation time. Retain old public verification material for the declared evidence-verification retention period where lawful.
- Revocation records reason, effective time, scope and whether compromise is suspected. A key revoked for routine rotation does not automatically invalidate signatures produced earlier; a compromise declaration triggers an explicit cutoff/reverification policy.
- If the signing authority is compromised or integrity cannot be checked, affected records are quarantined and cannot satisfy acceptance criteria until reviewed.
- Recovery/backup access to keys is controlled and audited; key rotation and restore procedures must be tested by the deployment profile before production.

## 6.4 Retention classes

Every record class maps to one retention policy containing purpose, legal basis/authority, max retention or review date, deletion method, legal-hold conditions and expected propagation scope. No universal fixed retention duration is imposed by PRAIN because lawful durations depend on data class, jurisdiction and purpose. `no expiry` is forbidden unless a documented legal/operational justification and review date exist. Logs, backups, derived claims and vector indexes receive explicit policies too.

## 6.5 Deletion workflow

`requested → approved → executing → verified` with side states `blocked_legal_hold`, `partially_verified`, `rejected`.

1. Authenticate requester and identify target record refs/tenant scope; prevent cross-tenant deletion.
2. Evaluate retention policy, legal holds and audit obligations. If a hold applies, record the narrowly scoped reason and do not claim deletion complete.
3. Tombstone the authoritative record and stop new reads/writes of the target version.
4. Propagate to replicas, event-derived state, projections, vector indexes, caches, exports, derived claims and external connectors according to the register.
5. Delete or cryptographically erase encrypted payload/content keys where appropriate. Backups expire within the declared backup horizon or are re-written/compacted under a documented procedure; restore workflows must reapply deletion tombstones before serving data.
6. Preserve only the minimum lawful deletion receipt/tombstone necessary for accountability; avoid retaining the deleted content or easily reversible personal hash in the tombstone.
7. Verify propagation by store/type and issue a deletion receipt listing checked targets, outstanding exceptions and backup expiry deadline. Completion is not `verified` while required stores are unchecked.

An append-only audit/evidence design does not justify retaining every payload forever. Separate immutable decision/deletion receipts from deletable content, minimize personal data in logs, and use key erasure where lawful and technically valid. Legal hold is an explicit exception with scope/review date, not a blanket veto over unrelated data.

## 6.6 Derived data and deletion

Every derived claim/index/projection must retain source references (or a privacy-preserving dependency token) sufficient to invalidate/rebuild when source data is deleted or corrected. The deletion manager propagates tombstones before restoring replicas/projections. Re-evaluate derived claims; delete or recompute them under policy. A vector-index delete is not enough if a text summary, embedding cache, backup or export retains reconstructable personal content.

## 6.7 Redaction and observability

Logs/traces must redact tokens, credentials, secret values and unrelated personal fields at collection, not just in dashboards. Retain minimal metadata that supports causal diagnosis and evidence. If mandatory audit events are dropped, record an audit-gap event/health signal; never state the audit trail is complete through a gap.
