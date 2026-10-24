"""Local durable tenant security: deny by default, scoped capabilities, revocation."""
import hmac
import hashlib
import secrets
import sqlite3
import time
from pathlib import Path


class AccessDenied(PermissionError):
    pass


class TenantAccess:
    def __init__(self, database):
        self.database = str(database)
        Path(database).parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS prain_principals (
                tenant TEXT NOT NULL, principal TEXT NOT NULL, token_digest TEXT NOT NULL,
                revoked INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(tenant,principal))""")
            db.execute("""CREATE TABLE IF NOT EXISTS prain_grants (
                tenant TEXT NOT NULL, principal TEXT NOT NULL, capability TEXT NOT NULL,
                resource TEXT NOT NULL, PRIMARY KEY(tenant,principal,capability,resource))""")

    def _db(self):
        return sqlite3.connect(self.database, timeout=15)

    @staticmethod
    def _valid(*items):
        if any(not isinstance(x, str) or not x.strip() for x in items):
            raise ValueError("nonempty string required")

    def provision(self, tenant, principal, capabilities):
        self._valid(tenant, principal)
        if not isinstance(capabilities, list) or not capabilities:
            raise ValueError("capabilities required")
        for capability, resource in capabilities:
            self._valid(capability, resource)
        token = secrets.token_urlsafe(32)
        digest = hashlib.sha256(token.encode()).hexdigest()
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT INTO prain_principals(tenant,principal,token_digest) VALUES(?,?,?)",
                       (tenant, principal, digest))
            for capability, resource in capabilities:
                db.execute("INSERT INTO prain_grants VALUES(?,?,?,?)", (tenant, principal, capability, resource))
        return token

    def authorize(self, tenant, principal, token, capability, resource):
        self._valid(tenant, principal, capability, resource)
        if not isinstance(token, str) or not token:
            raise AccessDenied("invalid_credentials")
        provided = hashlib.sha256(token.encode()).hexdigest()
        with self._db() as db:
            db.execute("BEGIN")
            row = db.execute("SELECT token_digest,revoked FROM prain_principals WHERE tenant=? AND principal=?",
                             (tenant, principal)).fetchone()
            allowed = db.execute("""SELECT 1 FROM prain_grants WHERE tenant=? AND principal=?
                                    AND capability=? AND resource=?""",
                                 (tenant, principal, capability, resource)).fetchone()
        if not row or row[1] or not hmac.compare_digest(row[0], provided) or not allowed:
            raise AccessDenied("access_denied")
        return True

    def revoke(self, tenant, principal):
        self._valid(tenant, principal)
        with self._db() as db:
            return db.execute("UPDATE prain_principals SET revoked=1 WHERE tenant=? AND principal=?",
                              (tenant, principal)).rowcount == 1

    def rotate(self, tenant, principal, current):
        self.authorize_identity(tenant, principal, current)
        replacement = secrets.token_urlsafe(32)
        digest = hashlib.sha256(replacement.encode()).hexdigest()
        old_digest = hashlib.sha256(current.encode()).hexdigest()
        with self._db() as db:
            result = db.execute("""UPDATE prain_principals SET token_digest=? WHERE tenant=? AND principal=?
                                   AND token_digest=? AND revoked=0""",
                                (digest, tenant, principal, old_digest))
            if result.rowcount != 1:
                raise AccessDenied("rotation_conflict")
        return replacement

    def authorize_identity(self, tenant, principal, token):
        self._valid(tenant, principal)
        if not isinstance(token, str) or not token:
            raise AccessDenied("invalid_credentials")
        with self._db() as db:
            row = db.execute("SELECT token_digest,revoked FROM prain_principals WHERE tenant=? AND principal=?",
                             (tenant, principal)).fetchone()
        if not row or row[1] or not hmac.compare_digest(row[0], hashlib.sha256(token.encode()).hexdigest()):
            raise AccessDenied("access_denied")
        return True
