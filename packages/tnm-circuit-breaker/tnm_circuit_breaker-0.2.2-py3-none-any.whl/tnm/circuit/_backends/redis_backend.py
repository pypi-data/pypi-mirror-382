import time
import uuid
from functools import cached_property
from typing import Any, Dict, cast

from redis import Redis
from redis.exceptions import NoScriptError

from .._redis import LuaScriptError, LuaScriptLoader
from ..exceptions import CircuitBackendError
from ..interfaces import CircuitBackend


class RedisCircuitBackend(CircuitBackend):
    """
    Key design:
    - failures zset key: "circuit:failures:{service}" where members are unique ids and scores are unix timestamps
    - meta hash key: "circuit:meta:{service}" stores last_failure_reason, last_failure_ts, count, etc.
    """

    def __init__(
        self,
        client: Redis,
        namespace: str = "circuit",
        meta_ttl_seconds: int = 0,
    ) -> None:
        self._client = client
        self._ns = namespace.strip(":")
        self._meta_ttl = int(meta_ttl_seconds)
        self._sha_record: str | None = None
        self._sha_reset: str | None = None
        self._sha_get_count: str | None = None
        self._initialized = False

    def initialize(self) -> None:
        try:
            self._sha_record = str(self._loader.load("circuit_failure_record", "sha"))
            self._sha_reset = str(self._loader.load("circuit_reset", "sha"))
            self._sha_get_count = str(self._loader.load("circuit_get_count", "sha"))
            self._initialized = True
        except LuaScriptError as e:
            raise CircuitBackendError(f"Failed to initialize lua scripts: {str(e)}")

    def _zkey(self, service: str) -> str:
        """Get the Redis key for the failures sorted set."""
        return f"{self._ns}:failures:{self._sanitize_service(service)}"

    def _hkey(self, service: str) -> str:
        """Get the Redis key for the metadata hash."""
        return f"{self._ns}:meta:{self._sanitize_service(service)}"

    def record_failure(
        self, service: str, reason: str, timestamp: float | None = None
    ) -> int:
        """Record a failure for the given service and return the failure count."""
        if not self._initialized:
            self.initialize()

        now = int(timestamp or time.time())
        cutoff = 0
        member = f"{now}:{uuid.uuid4().hex}"
        zkey = self._zkey(service)
        hkey = self._hkey(service)
        args = [member, str(now), str(cutoff), reason, str(self._meta_ttl)]

        try:
            result = self._client.evalsha(
                cast(str, self._sha_record), 2, zkey, hkey, *args
            )
        except NoScriptError:
            result = self._client.eval(
                str(self._loader.load("circuit_failure_record", "contents")),
                2,
                zkey,
                hkey,
                *args,
            )
        return int(cast(str, result))

    def record_success(self, service: str, timestamp: float | None = None) -> None:
        """Record a success for the given service."""
        if not self._initialized:
            self.initialize()

        ts = int(timestamp or time.time())
        zkey = self._zkey(service)
        hkey = self._hkey(service)

        try:
            self._client.evalsha(
                cast(str, self._sha_reset), 2, zkey, hkey, str(ts), str(self._meta_ttl)
            )
        except NoScriptError:
            self._client.eval(
                str(self._loader.load("circuit_reset", "contents")),
                2,
                zkey,
                hkey,
                str(ts),
                str(self._meta_ttl),
            )

    def get_failure_count(self, service: str, cutoff: int) -> int:
        """Get the number of failures for the given service since the cutoff time."""
        if not self._initialized:
            self.initialize()

        zkey = self._zkey(service)
        try:
            res = self._client.evalsha(
                cast(str, self._sha_get_count), 1, zkey, str(cutoff)
            )
        except NoScriptError:
            res = self._client.eval(
                str(self._loader.load("circuit_get_count", "contents")),
                1,
                zkey,
                str(cutoff),
            )
        return int(cast(str, res))

    def get_last_failure(self, service: str) -> Dict[str, Any] | None:
        """Get metadata about the last failure for the given service."""
        if not self._initialized:
            self.initialize()

        hkey = self._hkey(service)
        data = self._client.hgetall(hkey)

        if not data:
            return None

        if not isinstance(data, dict):
            return None

        def _to_str(value: Any) -> str:
            if isinstance(value, (bytes, bytearray, memoryview)):
                try:
                    # Use surrogateescape to preserve undecodable bytes instead of raising
                    return bytes(value).decode("utf-8", errors="surrogateescape")
                except Exception:
                    try:
                        return bytes(value).decode("latin-1", errors="replace")
                    except Exception:
                        return str(value)
            if isinstance(value, str):
                return value
            try:
                return str(value)
            except Exception:
                return repr(value)

        decoded: Dict[str, str] = {}
        for k, v in data.items():
            key_str = _to_str(k)
            val_str = _to_str(v)
            decoded[key_str] = val_str

        return decoded

    @cached_property
    def _loader(self) -> LuaScriptLoader:
        return LuaScriptLoader(redis=self._client)
