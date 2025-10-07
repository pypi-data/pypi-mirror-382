from unittest.mock import MagicMock

import httpx
import pytest

from tnm.circuit.exceptions import CircuitOpenError, ReturnValuePolicyError


@pytest.mark.asyncio
async def test_protect_async_short_circuits_when_open(mock_circuit_breaker):
    cb = mock_circuit_breaker

    pol = cb.policy_for("api")
    cb._backend.get_failure_count = lambda service, cutoff: pol.max_failures

    @cb.protect("api")
    async def decorated_ok():
        return "ok"

    with pytest.raises(
        CircuitOpenError,
        match="circuit is open for service 'api' due to 1 failure within 60 seconds",
    ):
        await decorated_ok()


@pytest.mark.asyncio
async def test_protect_async_records_on_exception_and_opens(mock_circuit_breaker):
    cb = mock_circuit_breaker

    @cb.protect("api")
    async def decorated_raises():
        raise httpx.ConnectError("boom-async")

    with pytest.raises(httpx.ConnectError, match="boom-async"):
        await decorated_raises()

    assert cb.is_available("api") is False

    last = cb.last_failure("api")
    assert isinstance(last, dict)
    assert "ConnectError" in last["reason"]

    with pytest.raises(
        CircuitOpenError,
        match="circuit is open for service 'api' due to 1 failure within 60 seconds",
    ):
        await decorated_raises()


@pytest.mark.asyncio
async def test_protect_async_ignores_ignored_exceptions(mock_circuit_breaker):
    cb = mock_circuit_breaker

    @cb.protect("api")
    async def decorated_ignored():
        raise httpx.HTTPStatusError("http status", request=None, response=None)

    with pytest.raises(httpx.HTTPStatusError):
        await decorated_ignored()

    assert cb.is_available("api") is True
    assert cb.last_failure("api") is None


@pytest.mark.asyncio
async def test_protect_async_returnval_policy_triggers(mock_circuit_breaker):
    cb = mock_circuit_breaker

    fake_resp = MagicMock()
    fake_resp.status_code = 500

    @cb.protect("api")
    async def decorated_retval():
        return fake_resp

    with pytest.raises(ReturnValuePolicyError):
        await decorated_retval()

    assert cb.is_available("api") is False
    last = cb.last_failure("api")
    assert isinstance(last, dict)
    assert last["reason"] == "return value in policy.retval_in ([500, 400, 503, 502])"

    with pytest.raises(
        CircuitOpenError,
        match="circuit is open for service 'api' due to 1 failure within 60 seconds",
    ):
        await decorated_retval()


def test_protect_sync_short_circuits_when_open(mock_circuit_breaker):
    cb = mock_circuit_breaker
    pol = cb.policy_for("api")
    cb._backend.get_failure_count = lambda service, cutoff: pol.max_failures

    @cb.protect("api")
    def decorated_ok():
        return "ok"

    with pytest.raises(CircuitOpenError):
        decorated_ok()


def test_protect_sync_records_on_exception_and_opens(mock_circuit_breaker):
    cb = mock_circuit_breaker

    @cb.protect("api")
    def decorated_raises():
        raise httpx.ConnectError("boom-sync")

    with pytest.raises(httpx.ConnectError, match="boom-sync"):
        decorated_raises()

    assert cb.is_available("api") is False
    last = cb.last_failure("api")
    assert isinstance(last, dict)
    assert "ConnectError" in last["reason"]

    with pytest.raises(CircuitOpenError):
        decorated_raises()


def test_protect_sync_ignores_ignored_exceptions(mock_circuit_breaker):
    cb = mock_circuit_breaker

    @cb.protect("api")
    def decorated_ignored():
        raise httpx.HTTPStatusError("http status", request=None, response=None)

    with pytest.raises(httpx.HTTPStatusError):
        decorated_ignored()

    assert cb.is_available("api") is True
    assert cb.last_failure("api") is None


def test_protect_sync_returnval_policy_triggers(mock_circuit_breaker):
    cb = mock_circuit_breaker

    fake_resp = MagicMock()
    fake_resp.status_code = 502

    @cb.protect("api")
    def decorated_retval():
        return fake_resp

    with pytest.raises(ReturnValuePolicyError):
        decorated_retval()

    assert cb.is_available("api") is False
    last = cb.last_failure("api")
    assert isinstance(last, dict)
    assert last["reason"] == "return value in policy.retval_in ([500, 400, 503, 502])"

    with pytest.raises(CircuitOpenError):
        decorated_retval()
