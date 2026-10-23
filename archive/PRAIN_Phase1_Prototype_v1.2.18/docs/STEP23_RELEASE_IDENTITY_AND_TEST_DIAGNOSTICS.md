# Step 23 — Release identity consistency and test diagnostics

## Changes
- Align the release directory name, README version, MANIFEST version/step, and release-integrity assertions.
- Add a regression test ensuring README and manifest version agree.
- Preserve honest acceptance status: targeted suites can pass while the full suite remains unverified.
- Keep the remaining ResourceWarning visible rather than claiming it is resolved.

## Acceptance
- Manifest/tree verifier must pass.
- Targeted backup/restore, backup bundle, runtime, dispatcher, and release-integrity tests must pass.
- Full-suite status remains PARTIAL_PASS until slow durable-admission/state-store/process tests complete in a supported environment.
