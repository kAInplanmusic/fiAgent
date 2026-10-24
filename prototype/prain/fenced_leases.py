"""SQLite local coordination with fencing tokens. No distributed consensus claim."""
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path


class LeaseRejected(ValueError):
    pass


@dataclass(frozen=True)
class Lease:
    resource: str
    owner: str
    token: int
    expires_at: float


class FencedLeaseStore:
    def __init__(self, db_path):
        self.path = str(db_path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._db() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS prain_leases(
                resource TEXT PRIMARY KEY, owner TEXT NOT NULL,
                token INTEGER NOT NULL, expires_at REAL NOT NULL)""")
            c.execute("""CREATE TABLE IF NOT EXISTS prain_fenced_values(
                resource TEXT PRIMARY KEY, token INTEGER NOT NULL,
                payload TEXT NOT NULL)""")

    def _db(self):
        return sqlite3.connect(self.path, timeout=15)

    @staticmethod
    def _check(resource, owner):
        if not isinstance(resource, str) or not resource.strip() or not isinstance(owner, str) or not owner.strip():
            raise LeaseRejected("resource_and_owner_required")

    def acquire(self, resource, owner, ttl, now=None):
        self._check(resource, owner)
        if type(ttl) not in (int, float) or not 0 < ttl <= 86400:
            raise LeaseRejected("invalid_ttl")
        import math
        if not math.isfinite(ttl):
            raise LeaseRejected("invalid_ttl")
        moment = time.time() if now is None else now
        if type(moment) not in (int, float) or not math.isfinite(moment):
            raise LeaseRejected("invalid_clock")
        with self._db() as c:
            c.execute("BEGIN IMMEDIATE")
            row = c.execute("SELECT owner,token,expires_at FROM prain_leases WHERE resource=?", (resource,)).fetchone()
            if row and moment < row[2]:
                raise LeaseRejected("lease_held")
            token = row[1] + 1 if row else 1
            expires = moment + ttl
            if not math.isfinite(expires):
                raise LeaseRejected("invalid_expiry")
            c.execute("""INSERT INTO prain_leases(resource,owner,token,expires_at) VALUES(?,?,?,?)
                ON CONFLICT(resource) DO UPDATE SET owner=excluded.owner,token=excluded.token,
                expires_at=excluded.expires_at""", (resource, owner, token, expires))
            return Lease(resource, owner, token, expires)

    def renew(self, lease, ttl, now=None):
        self._check(lease.resource, lease.owner)
        import math
        if type(ttl) not in (int, float) or not math.isfinite(ttl) or not 0 < ttl <= 86400:
            raise LeaseRejected("invalid_ttl")
        moment = time.time() if now is None else now
        if type(moment) not in (int, float) or not math.isfinite(moment):
            raise LeaseRejected("invalid_clock")
        with self._db() as c:
            c.execute("BEGIN IMMEDIATE")
            row = c.execute("SELECT owner,token,expires_at FROM prain_leases WHERE resource=?", (lease.resource,)).fetchone()
            if not row or row[0] != lease.owner or row[1] != lease.token or moment >= row[2]:
                raise LeaseRejected("stale_lease")
            expires = moment + ttl
            c.execute("UPDATE prain_leases SET expires_at=? WHERE resource=?", (expires, lease.resource))
            return Lease(lease.resource, lease.owner, lease.token, expires)

    def fenced_write(self, lease, payload, now=None):
        import math
        if not isinstance(lease, Lease) or not isinstance(payload, str):
            raise LeaseRejected("invalid_write")
        moment = time.time() if now is None else now
        if type(moment) not in (int, float) or not math.isfinite(moment):
            raise LeaseRejected("invalid_clock")
        with self._db() as c:
            c.execute("BEGIN IMMEDIATE")
            row = c.execute("SELECT owner,token,expires_at FROM prain_leases WHERE resource=?", (lease.resource,)).fetchone()
            if not row or row[0] != lease.owner or row[1] != lease.token or moment >= row[2]:
                raise LeaseRejected("stale_fencing_token")
            c.execute("""INSERT INTO prain_fenced_values(resource,token,payload) VALUES(?,?,?)
                ON CONFLICT(resource) DO UPDATE SET token=excluded.token,payload=excluded.payload
                WHERE excluded.token >= prain_fenced_values.token""", (lease.resource, lease.token, payload))
            return lease.token

    def read(self, resource):
        with self._db() as c:
            row = c.execute("SELECT token,payload FROM prain_fenced_values WHERE resource=?", (resource,)).fetchone()
        return row
