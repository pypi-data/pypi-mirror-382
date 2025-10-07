import time
from typing import Any

import pytest

redis = pytest.importorskip("redis")
Redis = redis.Redis

try:
    from tnm.circuit._backends.redis_backend import RedisCircuitBackend  # noqa
except ImportError:
    from tnm.circuit._backends.redis_backend import RedisCircuitBackend  # noqa


@pytest.fixture
def mock_redis():
    return FakeRedis()


class FakeRedis:
    def __init__(self):
        self._zsets: dict[str, dict[str, int]] = {}
        self._hashes: dict[str, dict[str, str]] = {}

    @staticmethod
    def ping():
        return True

    def zadd(self, key: str, mapping: dict[str, int]) -> int:
        s = self._zsets.setdefault(key, {})
        added = 0
        for member, score in mapping.items():
            if member not in s:
                added += 1
            s[member] = int(score)
        return added

    def zremrangebyscore(self, key: str, min_score: int, max_score: int) -> int:
        removed = 0
        s = self._zsets.get(key, {})
        to_remove = [m for m, sc in s.items() if min_score <= sc <= max_score]
        for m in to_remove:
            del s[m]
            removed += 1
        if not s:
            self._zsets.pop(key, None)
        return removed

    def zcard(self, key: str) -> int:
        return len(self._zsets.get(key, {}))

    def hset(self, key: str, mapping: dict[str, str]) -> int:
        h = self._hashes.setdefault(key, {})
        for k, v in mapping.items():
            h[k] = v
        return len(mapping)

    def hgetall(self, key: str) -> dict[bytes, bytes]:
        h = self._hashes.get(key, {})
        return {k.encode(): v.encode() for k, v in h.items()}

    def delete(self, *keys: str) -> int:
        removed = 0
        for k in keys:
            if k in self._zsets:
                del self._zsets[k]
                removed += 1
            if k in self._hashes:
                del self._hashes[k]
                removed += 1
        return removed

    def eval(self, script: str, numkeys: int, *keys_and_args: Any):
        return self._dispatch_eval(script, numkeys, *keys_and_args)

    def evalsha(self, sha: str, numkeys: int, *keys_and_args: Any) -> int:
        return self._dispatch_eval(sha, numkeys, *keys_and_args)

    def _dispatch_eval(self, script_name: str, numkeys: int, *keys_and_args: Any):
        keys = list(keys_and_args[:numkeys])
        args = list(keys_and_args[numkeys:])

        if script_name == "circuit_failure_record" or script_name.endswith(
            "circuit_failure_record"
        ):
            member, now_s, cutoff_s, reason, meta_ttl = args[:5]
            zkey = keys[0]
            hkey = keys[1]
            now = int(now_s)

            self.zadd(zkey, {member: now})

            self.hset(
                hkey, {"last_failure_reason": reason, "last_failure_ts": str(now)}
            )
            # return current zcard
            return self.zcard(zkey)

        if script_name == "circuit_reset" or script_name.endswith("circuit_reset"):
            # args = [ts, meta_ttl]
            zkey = keys[0]
            hkey = keys[1]
            # remove entire zset and meta
            self.delete(zkey)
            self.delete(hkey)
            # return 0
            return 0

        if script_name == "circuit_get_count" or script_name.endswith(
            "circuit_get_count"
        ):
            # args = [cutoff]
            zkey = keys[0]
            cutoff_s = args[0]
            cutoff = int(cutoff_s)
            # remove <= cutoff and return cardinality
            self.zremrangebyscore(zkey, -1_000_000_000, cutoff)
            return self.zcard(zkey)

        raise RuntimeError(f"Unknown script requested: {script_name}")


class DummyLuaLoader:
    def __init__(self, redis):
        self._redis = redis

    @staticmethod
    def load(name: str, field: str):  # noqa
        return name


@pytest.fixture(scope="function")
def redis_backend(mock_redis):
    fake = FakeRedis()
    backend = RedisCircuitBackend(fake, namespace="testcircuit", meta_ttl_seconds=0)
    setattr(backend, "_loader", DummyLuaLoader(fake))
    backend.initialize()
    return backend


def test_record_failure_and_count(redis_backend):
    svc = "redis-svc"
    ts_old = int(time.time() - 120)
    ts_new = int(time.time())
    c1 = redis_backend.record_failure(svc, "boom-old", timestamp=ts_old)
    assert isinstance(c1, int) and c1 >= 1
    c2 = redis_backend.record_failure(svc, "boom-now", timestamp=ts_new)
    assert isinstance(c2, int) and c2 >= 1

    cutoff = int(time.time() - 60)
    remaining = redis_backend.get_failure_count(svc, cutoff=cutoff)
    assert remaining == 1


def test_record_success_clears(redis_backend):
    svc = "svc-reset"
    redis_backend.record_failure(svc, "err1")
    assert redis_backend.get_failure_count(svc, cutoff=int(time.time() - 3600)) >= 1

    redis_backend.record_success(svc)
    assert redis_backend.get_failure_count(svc, cutoff=int(time.time() - 3600)) == 0
    assert redis_backend.get_last_failure(svc) is None


def test_last_failure_metadata(redis_backend):
    svc = "meta-svc"
    redis_backend.record_failure(svc, "meta-1", timestamp=int(time.time()))
    meta = redis_backend.get_last_failure(svc)
    assert isinstance(meta, dict)
    assert (
        "last_failure_reason" in meta or "reason" in meta
    )  # tolerant: depending on hash fields naming
    assert "last_failure_ts" in meta or "ts" in meta
