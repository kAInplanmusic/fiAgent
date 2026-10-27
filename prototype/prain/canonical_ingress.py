"""Authenticated, durable canonical inbox; stores facts as messages, not authority.

The service adapter injects current authentication (no default allow callback).
This inbox is separate from the legacy SCF projection contract and performs no
automatic lossy conversion, policy approval, fact promotion or side effect.
"""
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from .canonical_contracts import CanonicalContracts, ContractRejected, loads_strict


class CanonicalInbox:
    def __init__(self, database, *, authenticate, recipient=None, contracts=None):
        if not callable(authenticate):
            raise TypeError("current_authentication_callback_required")
        self.authenticate = authenticate
        self.recipient = recipient
        self.contracts = contracts or CanonicalContracts()
        self.database = str(database)
        Path(database).parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS prain_canonical_inbox (
                tenant TEXT NOT NULL, message_id TEXT NOT NULL, producer TEXT NOT NULL,
                request_digest TEXT NOT NULL, envelope TEXT NOT NULL,
                PRIMARY KEY(tenant,message_id))""")

    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.database, timeout=15)
        try:
            with db:
                yield db
        finally:
            db.close()

    def _identity(self, credential):
        identity = self.authenticate(credential)
        if (not isinstance(identity, tuple) or len(identity) != 2
                or any(not isinstance(x, str) or not x for x in identity)):
            raise PermissionError("authenticated_identity_required")
        return identity

    def accept(self, raw, *, credential, now):
        tenant, principal = self._identity(credential)
        envelope = self.contracts.validate_envelope(
            loads_strict(raw), authenticated_tenant=tenant,
            authenticated_principal=principal, now=now, expected_recipient=self.recipient)
        encoded = json.dumps(envelope, sort_keys=True, separators=(",", ":"), allow_nan=False)
        digest = sha256(encoded.encode()).hexdigest()
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("""SELECT request_digest FROM prain_canonical_inbox
                                WHERE tenant=? AND message_id=?""",
                             (tenant, envelope["message_id"])).fetchone()
            if row:
                if row[0] != digest:
                    raise ContractRejected("message_id_body_conflict")
                return {"message_id": envelope["message_id"], "request_digest": digest,
                        "status": "stored", "duplicate": True}
            db.execute("INSERT INTO prain_canonical_inbox VALUES(?,?,?,?,?)",
                       (tenant, envelope["message_id"], principal, digest, encoded))
        return {"message_id": envelope["message_id"], "request_digest": digest,
                "status": "stored", "duplicate": False}

    def get(self, message_id, *, credential):
        tenant, principal = self._identity(credential)
        with self._db() as db:
            row = db.execute("""SELECT envelope FROM prain_canonical_inbox
                WHERE tenant=? AND producer=? AND message_id=?""",
                (tenant, principal, message_id)).fetchone()
        return None if row is None else json.loads(row[0])
