import asyncio
from typing import Any
from unittest.mock import MagicMock

import pytest

from tnm.circuit.exceptions import ReturnValuePolicyError
from tnm.circuit.policies import ReturnValuePolicy


def _make_nested_obj(value: Any):
    inner = MagicMock()
    inner.code = value
    status = MagicMock()
    status.code = value

    meta = MagicMock()
    meta.status = status

    class Obj:
        def __init__(self, v):
            self.meta = MagicMock()
            self.meta.status = MagicMock()
            self.meta.status.code = v
            # also allow attribute chain via dict lookup
            self._d = {"meta": {"status": {"code": v}}}

        def __getattr__(self, name):
            return (
                getattr(self.__dict__[name], name)
                if name in self.__dict__
                else super().__getattribute__(name)
            )

        def to_dict(self):
            return self._d

    return Obj(value)


def _make_nested_dict(value):
    return {"meta": {"status": {"code": value}}}


def test_protect_override_retval_policy_sync_dotted_accessor(mock_circuit_breaker):
    cb = mock_circuit_breaker
    policy = ReturnValuePolicy(retval_in=[42], retval_accessor="meta.status.code")

    fake_resp = _make_nested_obj(42)

    @cb.protect("api", on_retval_policy=policy)
    def decorated_fn():
        return fake_resp

    with pytest.raises(ReturnValuePolicyError) as exc_info:
        decorated_fn()

    assert (
        exc_info.value.message
        == f"A failure was recorded for service 'api' because the return value '{fake_resp}' "
        "triggered the return value policy: return value in policy.retval_in ([42])"
    )

    assert cb.is_available("api") is False
    last = cb.last_failure("api")
    assert isinstance(last, dict)

    assert last["reason"] == "return value in policy.retval_in ([42])"


@pytest.mark.asyncio
async def test_execute_override_retval_policy_async_dotted_accessor(
    mock_circuit_breaker,
):
    cb = mock_circuit_breaker
    policy = ReturnValuePolicy(retval=777, retval_accessor="meta.status.code")

    async def call_async():
        await asyncio.sleep(0)
        return _make_nested_obj(777)

    with pytest.raises(ReturnValuePolicyError) as exc_info:
        await cb.execute_async("api", call_async, on_retval_policy=policy)

    assert (
        exc_info.value.message
        == f"A failure was recorded for service 'api' because the return value '{exc_info.value.retval}' "
        "triggered the return value policy: return value equals policy.retval (777)"
    )

    assert cb.is_available("api") is False
    last = cb.last_failure("api")
    assert isinstance(last, dict)

    assert last["reason"] == "return value equals policy.retval (777)"


def test_execute_override_on_dict_return_sync(mock_circuit_breaker):
    cb = mock_circuit_breaker
    policy = ReturnValuePolicy(retval_in=[9001], retval_accessor="meta.status.code")

    def call():
        return _make_nested_dict(9001)

    with pytest.raises(ReturnValuePolicyError):
        cb.execute("api", call, on_retval_policy=policy)

    assert cb.is_available("api") is False


@pytest.mark.asyncio
async def test_execute_override_on_dict_return_async(mock_circuit_breaker):
    cb = mock_circuit_breaker
    policy = ReturnValuePolicy(retval_in=[1337], retval_accessor="meta.status.code")

    async def call_async():
        await asyncio.sleep(0)
        return _make_nested_dict(1337)

    with pytest.raises(ReturnValuePolicyError):
        await cb.execute_async("api", call_async(), on_retval_policy=policy)

    assert cb.is_available("api") is False
