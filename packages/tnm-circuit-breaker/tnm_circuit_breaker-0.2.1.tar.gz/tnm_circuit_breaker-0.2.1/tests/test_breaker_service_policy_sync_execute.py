from unittest.mock import MagicMock

import httpx
import pytest

from tnm.circuit.exceptions import CircuitOpenError, ReturnValuePolicyError


@pytest.mark.parametrize(
    "exc_cls,msg",
    [
        (httpx.ConnectError, "connect error test"),
        (httpx.TimeoutException, "timeout test"),
        (httpx.NetworkError, "network error test"),
        (httpx.ConnectTimeout, "connect timeout test"),
    ],
)
def test_api_service_execute_param_exceptions_sync(mock_circuit_breaker, exc_cls, msg):
    cb = mock_circuit_breaker

    client = MagicMock(spec=httpx.Client)
    client.get.side_effect = exc_cls(msg)

    def make_get_request():
        return client.get("http://test.com")

    with pytest.raises(exc_cls, match=msg):
        cb.execute("api", make_get_request)

    assert cb.is_available("api") is False

    last = cb.last_failure("api")
    assert isinstance(last, dict)
    assert last["reason"] == f"{exc_cls.__name__}: {msg}"

    with pytest.raises(CircuitOpenError):
        cb.execute("api", make_get_request)


def test_ignored_exception_does_not_record_failure_sync(
    mock_circuit_breaker,
):
    cb = mock_circuit_breaker
    client = MagicMock(spec=httpx.Client)

    client.get.side_effect = httpx.HTTPStatusError(
        "HTTP status error", request=None, response=None
    )

    def make_get_request():
        return client.get("http://test.com")

    with pytest.raises(httpx.HTTPStatusError):
        cb.execute("api", make_get_request)

    assert cb.is_available("api") is True
    assert cb.last_failure("api") is None


def test_retval_policy_triggers_and_records_failure_sync(
    mock_circuit_breaker,
):
    cb = mock_circuit_breaker
    client = MagicMock(spec=httpx.Client)

    fake_response = MagicMock()
    fake_response.status_code = 500

    client.get.return_value = fake_response

    def make_get_request():
        return client.get("http://test.com")

    with pytest.raises(ReturnValuePolicyError):
        cb.execute("api", make_get_request)

    assert cb.is_available("api") is False

    last = cb.last_failure("api")
    assert isinstance(last, dict)
    assert "return value" in last["reason"] or "retval" in last["reason"]

    with pytest.raises(CircuitOpenError):
        cb.execute("api", make_get_request)
