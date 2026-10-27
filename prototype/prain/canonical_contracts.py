"""Offline, integrity-bound canonical v0.99.6 validation; grants no authority.

Dependencies are explicit in requirements-canonical.txt. Missing dependency,
unknown schemas and incompatible versions fail closed. Historical SCFClaim is
not silently promoted or projected into the richer canonical claim contract.
"""
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from hashlib import sha256
import json
import math
from pathlib import Path
import re


CONTRACT_ROOT = Path(__file__).resolve().parents[1] / "contracts" / "v0.99.6"
MANIFEST_SHA256 = "e27f53f997d9d328ded6b56046886bd29ce16c26661b993eb019f9ba13c1c8ff"
_DATE_TIME = re.compile(r"^\d{4}-\d\d-\d\d[Tt]\d\d:\d\d:\d\d(?:\.\d+)?(?:[Zz]|[+-]\d\d:\d\d)$")


class ContractRejected(ValueError):
    """Malformed or unsupported input. No write may precede this check."""


def _datetime(value):
    if not isinstance(value, str) or not _DATE_TIME.fullmatch(value):
        raise ValueError("rfc3339_timestamp_required")
    parsed = datetime.fromisoformat(value.upper().replace("Z", "+00:00"))
    if parsed.utcoffset() != timedelta(0) or value.endswith("-00:00"):
        raise ValueError("explicit_utc_timestamp_required")
    return parsed


def _json_value(value, depth=0, budget=None):
    budget = [10000] if budget is None else budget
    budget[0] -= 1
    if depth > 32 or budget[0] < 0:
        raise ContractRejected("json_structure_limit")
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ContractRejected("finite_json_numbers_required")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise ContractRejected("string_json_keys_required")
            _json_value(item, depth + 1, budget)
        return
    if type(value) is list:
        for item in value:
            _json_value(item, depth + 1, budget)
        return
    raise ContractRejected("json_types_required")


def _canonical(value):
    _json_value(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def loads_strict(raw):
    """Parse bounded JSON without duplicate keys or non-finite extensions."""
    if not isinstance(raw, bytes) or len(raw) > 65536:
        raise ContractRejected("bounded_json_bytes_required")
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ContractRejected("duplicate_json_key")
            value[key] = item
        return value
    def constant(_value):
        raise ContractRejected("finite_json_numbers_required")
    try:
        value = json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
        _json_value(value)
        return value
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ContractRejected("invalid_json") from exc


class CanonicalContracts:
    def __init__(self, directory=CONTRACT_ROOT):
        try:
            from jsonschema import Draft202012Validator, FormatChecker
        except ImportError as exc:
            raise RuntimeError("canonical_jsonschema_dependency_required") from exc
        self._schemas = {}
        self._validators = {}
        directory = Path(directory)
        manifest_bytes = (directory / "MANIFEST.json").read_bytes()
        if sha256(manifest_bytes).hexdigest() != MANIFEST_SHA256:
            raise ContractRejected("canonical_manifest_integrity_mismatch")
        manifest = json.loads(manifest_bytes)
        checker = FormatChecker()

        @checker.checks("date-time", raises=(ValueError, TypeError))
        def date_time(value):
            if not isinstance(value, str):
                return True  # Type restriction belongs to the schema.
            _datetime(value)
            return True

        for filename, entry in manifest["files"].items():
            raw = (directory / filename).read_bytes()
            if sha256(raw).hexdigest() != entry["sha256"]:
                raise ContractRejected("canonical_contract_integrity_mismatch:" + filename)
            if not filename.endswith(".schema.json"):
                continue
            schema = json.loads(raw)
            Draft202012Validator.check_schema(schema)
            name = filename.removesuffix(".schema.json")
            self._schemas[name] = schema
            validator = Draft202012Validator(schema, format_checker=checker)
            self._validators[name] = validator
            self._validators[schema["$id"]] = validator

    @property
    def names(self):
        return tuple(sorted(self._schemas))

    def schema(self, name):
        if name not in self._validators:
            raise ContractRejected("unsupported_schema")
        return deepcopy(self._validators[name].schema)

    def validate(self, name, value):
        """Return detached validated JSON; do not imply provenance or authorization."""
        if name not in self._validators:
            raise ContractRejected("unsupported_schema")
        encoded = _canonical(value)
        if len(encoded) > 65536:
            raise ContractRejected("canonical_payload_size_limit")
        detached = json.loads(encoded)
        error = next(self._validators[name].iter_errors(detached), None)
        if error:
            pointer = "/" + "/".join(str(x) for x in error.absolute_path)
            raise ContractRejected("schema_violation:" + pointer + ":" + error.validator)
        return detached

    def validate_envelope(self, envelope, *, authenticated_tenant,
                          authenticated_principal, now, expected_recipient=None):
        """Validate both contracts plus authenticated scope/freshness before mutation.

        Credentials and current capabilities must already have been checked by
        the caller. A valid schema never authorizes an action or verifies a fact.
        """
        value = self.validate("message-envelope", envelope)
        if (not isinstance(authenticated_tenant, str) or not authenticated_tenant
                or not isinstance(authenticated_principal, str) or not authenticated_principal
                or value["tenant_id"] != authenticated_tenant
                or value["producer_principal_id"] != authenticated_principal):
            raise ContractRejected("authenticated_envelope_scope_mismatch")
        if expected_recipient is not None and value.get("recipient_principal_id") != expected_recipient:
            raise ContractRejected("recipient_mismatch")
        current = _datetime(now)
        if _datetime(value["created_at"]) > current + timedelta(seconds=30):
            raise ContractRejected("future_envelope")
        if "expires_at" in value and (_datetime(value["expires_at"]) <= current
                or _datetime(value["expires_at"]) <= _datetime(value["created_at"])):
            raise ContractRejected("expired_or_invalid_envelope_interval")
        schema_id = value["schema_id"]
        schema = self.schema(schema_id)
        declared_version = schema.get("properties", {}).get("schema_version", {}).get("const")
        if not declared_version or value["payload_schema_version"] != declared_version:
            raise ContractRejected("payload_schema_version_mismatch")
        payload = self.validate(schema_id, value["payload"])
        if payload.get("tenant_id") != authenticated_tenant:
            raise ContractRejected("payload_tenant_mismatch")
        classes = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}
        if ("classification" in payload
                and classes[value["classification"]] < classes[payload["classification"]]):
            raise ContractRejected("envelope_classification_downgrade")
        value["payload"] = payload
        return value


def quarantine_legacy_claim(value, *, source_schema_id, source_version, source_ref):
    """Named deterministic lossless quarantine rule, never an authority migration.

    All legacy states (including `verified`) remain unpromoted until an explicit
    complete mapping with provenance/tenant authority is available. Original
    bytes are represented by a canonical JSON snapshot and digest, not invented
    timestamps or factual provenance. No canonical claim is emitted.
    """
    if (source_schema_id != "https://prain.dev/schema/claim-0.1.0.json"
            or source_version != "0.1.0" or not isinstance(source_ref, str) or not source_ref):
        raise ContractRejected("unregistered_legacy_migration")
    if not isinstance(value, dict) or not isinstance(value.get("id"), str) or not value["id"]:
        raise ContractRejected("legacy_claim_identity_required")
    raw = _canonical(value)
    if len(raw) > 65536:
        raise ContractRejected("legacy_payload_size_limit")
    return {"rule_version": "legacy-claim-lossless-quarantine:1.0.0",
            "source_schema_id": source_schema_id, "source_version": source_version,
            "source_ref": source_ref, "target_schema_id": "urn:prain:schema:claim:1.0.0",
            "target_version": "1.0.0", "deterministic": True, "reversible": True,
            "lossy_fields": [], "defaults": {}, "status": "quarantined",
            "rejection_conditions": ["unregistered_source_schema_or_version", "missing_legacy_id", "non_json_or_over_budget_input"],
            "fixtures": ["test_canonical_contracts.CanonicalContractTests.test_legacy_unknown_and_verified_are_losslessly_quarantined"],
            "reason": "explicit_tenant_provenance_and_verification_mapping_required",
            "legacy_id": value["id"], "legacy_verification": value.get("verification_status"),
            "source_sha256": sha256(raw).hexdigest(), "source_snapshot": json.loads(raw),
            "canonical_claim": None, "source_validation": "NOT_PERFORMED_QUARANTINED_INPUT"}
