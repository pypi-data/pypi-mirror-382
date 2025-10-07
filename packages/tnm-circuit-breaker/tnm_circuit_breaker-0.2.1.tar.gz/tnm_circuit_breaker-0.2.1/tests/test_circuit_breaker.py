import time
from unittest.mock import MagicMock

import pytest

from src.tnm.circuit import CircuitBreaker
from src.tnm.circuit.policies import ServicePolicy


def test_is_available_and_recording(
    mock_circuit_breaker: CircuitBreaker, sqlite_backend
):
    policy = ServicePolicy(window_seconds=60, max_failures=2)
    cb = mock_circuit_breaker

    assert cb.is_available("svc-x") is True

    cnt1 = cb.record_failure("svc-x", "err1", timestamp=int(time.time()))
    assert isinstance(cnt1, int)
    cnt2 = cb.record_failure("svc-x", "err2", timestamp=int(time.time()))
    assert isinstance(cnt2, int)

    avail = cb.is_available("svc-x")
    assert avail == (
        sqlite_backend.get_failure_count(
            "svc-x", cutoff=int(time.time() - policy.window_seconds)
        )
        < policy.max_failures
    )


@pytest.mark.asyncio
async def test_execute_records_success_and_failure(mock_circuit_breaker):
    cb = mock_circuit_breaker

    async def ok_coro():
        return "done"

    res = await cb.execute_async("svc", ok_coro())
    assert res == "done"

    cb.record_failure = MagicMock(side_effect=cb.record_failure)

    async def fail_coro():
        raise ValueError("fail")

    with pytest.raises(ValueError):
        await cb.execute_async("svc", fail_coro())

    assert cb.record_failure.call_count >= 1


def test_decorator_resolves_policy_at_decoration_time(
    monkeypatch, mock_circuit_breaker
):
    monkeypatch.setattr(
        "src.tnm.circuit._breaker.effective_policy_overrides",
        lambda *a, **kw: ((), (), None),
    )

    cb = mock_circuit_breaker

    @cb.protect("svc", on_retval_policy=None)
    async def myfunc():
        return "ok"
