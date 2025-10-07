import logging
import time
import uuid
from functools import cached_property
from pathlib import Path
from sqlite3 import Connection, Row, connect as sqlite_connect
from typing import Any, Mapping, Protocol

from .._path import PACKAGE_DIR
from .._typeguard import typechecked
from ..exceptions import CircuitBackendError
from ..interfaces import CircuitBackend

logger = logging.getLogger("circuit.sqlite")


class _ConnectionMgr(Protocol):
    _db: str | Path

    def connect(self) -> Connection: ...

    def close(self) -> None: ...


class _ConnectionManager:
    def __init__(self, db: str | Path) -> None:
        self._db = db
        self._conn: Connection | None = None

    def connect(self) -> Connection:
        if self._conn is not None:
            return self._conn

        if isinstance(self._db, Path):
            self._db.parent.mkdir(parents=True, exist_ok=True)

        path_arg = str(self._db)
        self._conn = sqlite_connect(path_arg, timeout=5, check_same_thread=False)
        self._conn.row_factory = Row
        return self._conn

    def close(self) -> None:
        if self._conn is None:
            return
        try:
            self._conn.close()
        except Exception as exc:
            logger.exception("Failed to close sqlite connection.", exc)
        finally:
            self._conn = None


@typechecked
class SQLiteCircuitBackend(CircuitBackend):
    def __init__(
        self,
        pragmas: dict | None = None,
        connection_manager: _ConnectionMgr | None = None,
    ) -> None:
        self._conn: Connection | None = None
        self._pragmas = {
            **{"journal_mode": "WAL", "synchronous": "NORMAL"},
            **(pragmas or {}),
        }
        self._provided_conn_manager = connection_manager
        self._initialized = False

    @cached_property
    def _db_path(self) -> Path:
        return PACKAGE_DIR.joinpath("storage", "db", "circuit.db")

    def _get_conn_manager(self) -> _ConnectionMgr:
        if self._provided_conn_manager is not None:
            return self._provided_conn_manager
        return _ConnectionManager(self._db_path)

    def _connect(self) -> Connection:
        mgr = self._get_conn_manager()
        return mgr.connect()

    def initialize(self) -> None:
        try:
            self._conn = self._connect()
            cur = self._conn.cursor()

            for k, v in self._pragmas.items():
                cur.execute(f"PRAGMA {k} = {v}")

            cur.execute(self._create_failures_table_sql)
            cur.execute(self._create_meta_table_sql)

            self._conn.commit()
            self._initialized = True
        except Exception as exc:
            raise CircuitBackendError(
                f"Failed to initialize sqlite backend: {str(exc)}"
            ) from exc

    def destroy(self) -> None:
        if not self._initialized or self._conn is None:
            return

        try:
            self._conn.execute("DROP TABLE IF EXISTS failures")
            self._conn.execute("DROP TABLE IF EXISTS meta")
            self._conn.commit()
        except Exception as exc:
            logger.exception("Failed to drop tables.", exc)
        finally:
            self._conn.close()
            self._conn = None
            self._initialized = False

    def record_failure(
        self, service: str, reason: str, timestamp: float | None = None
    ) -> int:
        if not self._initialized or self._conn is None:
            self.initialize()
            assert self._conn is not None
        assert self._conn is not None

        ts = int(timestamp or time.time())
        member = f"{ts}:{uuid.uuid4().hex}"
        svc = self._sanitize_service(service)
        try:
            cur = self._conn.cursor()
            cur.execute(
                "INSERT OR IGNORE INTO failures (service, member, ts, reason) VALUES (?, ?, ?, ?)",
                (svc, member, ts, reason),
            )
            cur.execute(
                "INSERT OR REPLACE INTO meta (service, last_failure_reason, last_failure_ts) VALUES (?, ?, ?)",
                (svc, reason, ts),
            )
            self._conn.commit()
            cur.execute(
                "SELECT COUNT(*) as cnt FROM failures WHERE service = ?", (svc,)
            )
            row = cur.fetchone()
            return int(row["cnt"]) if row else 0
        except Exception as exc:
            raise CircuitBackendError(f"Failed to record failure: {str(exc)}") from exc

    def record_success(self, service: str, timestamp: float | None = None) -> None:
        if not self._initialized or self._conn is None:
            self.initialize()
            assert self._conn is not None

        svc = self._sanitize_service(service)
        try:
            cur = self._conn.cursor()
            cur.execute("DELETE FROM failures WHERE service = ?", (svc,))
            cur.execute("DELETE FROM meta WHERE service = ?", (svc,))
            self._conn.commit()
        except Exception as exc:
            raise CircuitBackendError(f"Failed to record success: {str(exc)}") from exc

    def get_failure_count(self, service: str, cutoff: int) -> int:
        if not self._initialized or self._conn is None:
            self.initialize()
            assert self._conn is not None
        svc = self._sanitize_service(service)
        try:
            cur = self._conn.cursor()
            cur.execute(
                "DELETE FROM failures WHERE service = ? AND ts <= ?", (svc, int(cutoff))
            )
            self._conn.commit()
            cur.execute(
                "SELECT COUNT(*) as cnt FROM failures WHERE service = ?", (svc,)
            )
            row = cur.fetchone()
            return int(row["cnt"]) if row else 0
        except Exception as exc:
            raise CircuitBackendError(
                f"Failed to get failure count: {str(exc)}"
            ) from exc

    def get_last_failure(self, service: str) -> Mapping[str, Any] | None:
        if not self._initialized or self._conn is None:
            self.initialize()
            assert self._conn is not None
        assert self._conn is not None
        svc = self._sanitize_service(service)
        try:
            cur = self._conn.cursor()
            cur.execute(
                "SELECT last_failure_reason, last_failure_ts FROM meta WHERE service = ?",
                (svc,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {"reason": row["last_failure_reason"], "ts": row["last_failure_ts"]}
        except Exception as exc:
            raise CircuitBackendError(
                f"Failed to fetch last failure: {str(exc)}"
            ) from exc

    def close(self) -> None:
        mgr = self._provided_conn_manager or _ConnectionManager(self._db_path)
        try:
            mgr.close()
        finally:
            self._conn = None
            self._initialized = False

    @cached_property
    def _create_failures_table_sql(self) -> str:
        return """
                CREATE TABLE IF NOT EXISTS failures (
                    service TEXT NOT NULL,
                    member TEXT NOT NULL PRIMARY KEY,
                    ts INTEGER NOT NULL,
                    reason TEXT
                );""".strip()

    @cached_property
    def _create_meta_table_sql(self) -> str:
        return """
                CREATE TABLE IF NOT EXISTS meta (
                    service TEXT PRIMARY KEY,
                    last_failure_reason TEXT,
                    last_failure_ts INTEGER
                );""".strip()
