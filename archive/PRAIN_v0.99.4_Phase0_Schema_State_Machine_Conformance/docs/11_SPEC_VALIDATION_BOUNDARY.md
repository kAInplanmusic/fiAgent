# 11. Offline validator boundary

`tools/validate_phase0.py` is a local specification/artefact validator. It does not import an agent runtime, connect to a broker/database, call external APIs, or perform tool actions. It validates JSON Schema meta-schemas, canonical fixture acceptance/rejection, JSON↔HTML data parity, knowledge-base references, source-archive integrity and selected deterministic invariants. Passing proves the package conforms to these tests only. It is not a production-security certification, penetration test, independent architecture review or legal compliance opinion.
