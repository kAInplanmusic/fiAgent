# Canonical contracts and authenticated durable ingress

This checkpoint executes the full 17 canonical Draft 2020-12 contracts from
`archive/PRAIN_v0.99.6_Phase0_Green_Closure.zip`, without changing schema bytes.
The bundled contract manifest binds each archive member, its hash and the source
archive hash. The Python module also pins the manifest hash, so updating both a
schema and its adjacent manifest cannot silently weaken validation.

`CanonicalContracts.validate(name_or_urn, payload)` validates strict bounded JSON
with actual `jsonschema.Draft202012Validator`, including every conditional and
nested constraint. Unknown schema IDs are rejected before lookup; this registry
does not fetch external schemas. Values/schemas returned to callers are detached.
No schema success establishes actual evidence integrity, authority, policy or
fact verification.

The explicit runtime ingress is `CanonicalInbox(database, authenticate=callback)`.
Its `accept(raw_json_bytes, credential=..., now=utc_rfc3339)` authenticates each
request, including duplicates, validates envelope **and** the declared typed
payload, binds tenant/producer and payload version, enforces expiry/future bounds,
and prohibits an envelope classification below the payload's explicit class.
Only then does one SQLite transaction store the complete canonical envelope and
payload. Duplicate identical messages reuse storage; an existing message ID with
a changed body fails closed. Reads reauthenticate and require the same producer
and tenant. Independent-connection race tests store one logical message.

The callback is the trusted service adapter's current authentication/authorization
check and must return the verified `(tenant, principal)` tuple. There is no default
allow callback. Tests use actual `TenantAccess.authorize()` and test wrong tokens,
revoked-token replay, tenant/producer spoofing and invalid-payload no-write cases.
This local inbox does not make revocation atomic with another process or external
effects. It stores messages; it neither grants policy nor promotes facts.

The historical SCF projection remains a different contract. No fields are dropped
to force canonical claims into `SemanticClaim`. This new canonical ingress is
exercised directly with durable integration tests; the existing HTTP SCF endpoint
is not falsely described as using it.

## Compatibility profile and migration limit

In addition to unchanged schema constraints, the boundary explicitly rejects
duplicate JSON keys, non-finite numbers, non-JSON Python types, payloads over64KiB,
more than10000 JSON nodes or depth32. UTC timestamps use `Z` or `+00:00`; nonzero
offsets, unknown `-00:00` offsets, naive timestamps and leap seconds are rejected.
These are explicit strict-profile rejections, not silent schema compatibility
claims. Future envelopes allow30seconds clock tolerance; version ordering remains
independent of clocks.

The named `legacy-claim-lossless-quarantine:1.0.0` rule preserves the entire legacy
claim snapshot, ID, verification label and digest. The actual historical schema ID
is `https://prain.dev/schema/claim-0.1.0.json`, including in the v0.2.1 package.
Unknown verification states and even legacy `verified` never create a verified
canonical claim. The quarantine explicitly records that legacy schema validation
was not performed. Complete migration executors and lossless/lossy canonical
translation fixtures are still separate obligations; this conservative quarantine
does not close the entire migration gate.

## Reproducible offline dependency installation

The baseline system Python has no `jsonschema`; absence raises
`canonical_jsonschema_dependency_required` rather than skipping or weakening checks.
The six dependency wheels and their hashes are included. The RPDS wheel supports
CPython3.12 on Linuxx86_64/manylinux2014. Other Python/platform combinations need
their own explicitly pinned compatible wheel set; cross-platform support is not
implied. Upstream licenses/metadata remain inside the unmodified wheels.

From the repository root, with Python3.12:

```sh
python3 -m venv /absolute/canonical-venv
/absolute/canonical-venv/bin/python -m pip install --no-index --find-links prototype/vendor/canonical-wheels --require-hashes -r prototype/requirements-canonical-hashed.txt
cd prototype
/absolute/canonical-venv/bin/python -m unittest discover -s tests -p test_canonical_contracts.py -v
```

A fresh isolated venv installation from the wheels was executed without index
access. The earlier 16-method targeted run is historical evidence; the completed
integration checkpoint now contains 259 successful unittest methods, zero failures,
zero errors and zero skips, both locally and on the PRAIN server. The prototype
release manifest covers137 files. Runtime checkpoint commits are local `e47f9e5`
and server `5c1059e`; normative disposition commits are local `7b2282f` and
server `fa98bca`. These are checkpoint identities, not production approvals.

The actual full-run reports are:

| Environment | Python | Seconds | Evidence |
|---|---|---:|---|
| Local | 3.12.14 | 20.217 | `evidence/canonical_full_suite/results.json` |
| PRAIN server | 3.12.3 | 29.733 | `evidence/canonical_server_suite/results.json` |

Their SHA-256 values are respectively
`717ba802cce6410dd94e8beb55444d33f85eb98f8bf47eea55ae2135b7d37181` and
`2b89a784548ac7f4e9871000e220aad695344f113085f2e05926996b3a3f201d`.
All recorded `prototype/` source hashes match across the two runs. Whole-repository
digests differ with documentation/metadata snapshots; the reports preserve those
actual digests. Individual fixture subtests are not counted as independent
unittest methods. Independent review identified and retested classification
downgrade protection. Executing the same single-host process suite in two
environments does not establish communication between two real hosts.

All5002 historical candidate rows now have contextual dispositions:2554 RETAIN,
2331 NON_NORMATIVE,47 SUPERSEDE and70 EXTEND. Their implementation assessment
is651 OPEN,2061 PARTIAL and2290 NA. This is not complete independent normative
acceptance. The independent semantic review of the complete applicable requirement
set and requirement-to-code-to-passing-test proofs remain release blockers.

Still open: direct network service wiring for this new ingress, whole-system
graph/transition semantics, externally anchored provenance/evidence verification,
all storage retention/deletion propagation, all migration families, real two-host
operations and final authorized release acceptance.
