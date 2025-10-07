from unittest.mock import MagicMock

import httpx
import pytest

from tnm.circuit.exceptions import CircuitOpenError, ReturnValuePolicyError


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exc_cls,msg",
    [
        (httpx.ConnectError, "connect error test"),
        (httpx.TimeoutException, "timeout test"),
        (httpx.NetworkError, "network error test"),
        (httpx.ConnectTimeout, "connect timeout test"),
    ],
)
async def test_api_service_execute_async_param_exceptions(
    mock_circuit_breaker, mock_http_async_client, exc_cls, msg
):
    cb = mock_circuit_breaker
    client = mock_http_async_client
    client.get.side_effect = exc_cls(msg)

    async def make_get_request():
        async with client as c:
            return await c.get("http://test.com")

    # first call raises the original exception
    with pytest.raises(exc_cls, match=msg):
        await cb.execute_async("api", make_get_request)

    # circuit should now be open
    assert cb.is_available("api") is False

    last = cb.last_failure("api")
    assert isinstance(last, dict)
    assert last["reason"] == f"{exc_cls.__name__}: {msg}"

    # second call should short-circuit
    with pytest.raises(CircuitOpenError):
        await cb.execute_async("api", make_get_request)


@pytest.mark.asyncio
async def test_ignored_exception_does_not_record_failure(
    mock_circuit_breaker, mock_http_async_client
):
    """
    Errors in ignore_exceptions should be re-raised but NOT recorded.
    Circuit remains available after such exceptions.
    """
    cb = mock_circuit_breaker
    client = mock_http_async_client

    client.get.side_effect = httpx.HTTPStatusError(
        "HTTP status error", request=None, response=None
    )

    async def make_get_request():
        async with client as c:
            return await c.get("http://test.com")

    with pytest.raises(httpx.HTTPStatusError):
        await cb.execute_async("api", make_get_request)

    assert cb.is_available("api") is True
    assert cb.last_failure("api") is None


@pytest.mark.asyncio
async def test_retval_policy_triggers_and_records_failure(
    mock_circuit_breaker, mock_http_async_client
):
    """
    When the client returns a response with a status_code in policy.retval_in,
    the breaker should record a failure and raise ReturnValuePolicyError.
    """
    cb = mock_circuit_breaker
    client = mock_http_async_client

    fake_response = MagicMock()
    fake_response.status_code = 500

    client.get.return_value = fake_response

    async def make_get_request():
        async with client as c:
            return await c.get("http://test.com")

    with pytest.raises(
        ReturnValuePolicyError, match="return value in policy.retval_in"
    ):
        await cb.execute_async("api", make_get_request)

    # circuit should now be open (max_failures == 1)
    assert cb.is_available("api") is False

    # last failure reason should mention return value / retval_in
    last = cb.last_failure("api")
    assert isinstance(last, dict)
    assert "return value" in last["reason"] or "policy.retval_in" in last["reason"]

    # subsequent call should be short-circuited
    with pytest.raises(
        CircuitOpenError,
        match="circuit is open for service 'api' due to 1 failure within 60 seconds",
    ):
        await cb.execute_async("api", make_get_request)
