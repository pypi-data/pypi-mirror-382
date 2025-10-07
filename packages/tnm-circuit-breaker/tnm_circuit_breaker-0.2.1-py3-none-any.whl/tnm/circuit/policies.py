from dataclasses import dataclass
from typing import Iterable, Optional

from ._typeguard import typechecked


_ReturnValueOf = int | str | bool | Iterable


@typechecked
@dataclass(frozen=True)
class ReturnValuePolicy:
    """
    Policy describing which *return values* from a protected call should be treated
    as *failures* by the circuit breaker.

    The policy can match on:
      * the returned value being `None` (`retval_none`),
      * equality against a single sentinel (`retval`),
      * membership in a collection (`retval_in`),
      * or an extracted value computed from the result via a dotted `retval_accessor`
        (see below).

    At least one of `retval_none`, `retval`, `retval_in`, or `retval_accessor` (or
    accessor args/kwargs) **must** be provided; otherwise the constructor raises
    :class:`~.exceptions.CircuitError`.

    Parameters
    ----------
    retval_none : bool | None
        If True, a returned value of ``None`` is considered a failure. If None
        (default) this rule is not applied.
    retval : int | str | bool | Iterable | None
        If provided, any returned value that is equal (``==``) to this value will
        be considered a failure. Equality comparison is used; if the comparison
        raises, it is ignored (treated as non-matching).
    retval_in : Iterable[int|str|bool|Iterable] | None
        If provided, and if ``result in retval_in`` (or equals an item in the
        iterable), the returned value is considered a failure. The implementation
        is tolerant of unhashable elements: if direct membership raises
        ``TypeError``, a linear scan using ``==`` is attempted. If ``retval_in``
        is not iterable, it will be ignored.
    retval_accessor : str | None
        Optional dotted accessor applied to the function result before evaluation.
        When provided, the policy checks are applied to the *accessed* value
        rather than to the raw result.

        The accessor string is a dot-separated path, e.g.:
          - `"status_code"` (access attribute or dict key `status_code`)
          - `"data.status"` (first access `result.data`, then `.status` or `['status']`)
          - `"get_status"` (if `get_status` is a method, it will be called if no
            accessor args/kwargs are supplied — see below)

        If accessor resolution or the call raises, accessor resolution is treated
        as failed and the original raw result is used for checks (no exception is
        propagated from accessor lookup).

    retval_accessor_args : tuple | None
        Optional positional arguments to pass when the final accessor resolves to
        a callable. Defaults to None (no args).
    retval_accessor_kwargs : dict | None
        Optional keyword arguments to pass when the final accessor resolves to
        a callable. Defaults to None (no kwargs).

    Examples
    --------
    Simple policies:
    >>> ReturnValuePolicy(retval_none=True)
    >>> ReturnValuePolicy(retval=0)
    >>> ReturnValuePolicy(retval_in=["", False, "error"])

    Using an accessor:
    - Suppose `result` is a `requests.Response` instance and you want to treat
      `status_code` 500 as failure:
      >>> ReturnValuePolicy(retval_accessor="status_code", retval_in=[500])

    - Suppose `result` is a dict like `{"data": {"status": "error"}}`:
      >>> ReturnValuePolicy(retval_accessor="data.status", retval="error")

    - Suppose the result exposes a method `get_status(code=False)` that returns an
      int and, you want to call it:
      >>> ReturnValuePolicy(
      ...     retval_accessor="get_status",
      ...     retval_accessor_args=(),
      ...     retval_accessor_kwargs={"code": True},
      ...     retval_in=[500, 502]
      ... )

    Note
    ----
    - Accessor invocation may execute user code (callable accessors). Use with
      care: the accessor is called inside the package process.
    """

    retval_none: bool | None = None
    retval: _ReturnValueOf | None = None
    retval_in: Iterable[_ReturnValueOf] | None = None
    retval_accessor: str | None = None
    retval_accessor_args: tuple | None = None
    retval_accessor_kwargs: dict | None = None

    def __post_init__(self):
        if all(
            x is None
            for x in (
                self.retval_none,
                self.retval,
                self.retval_in,
                self.retval_accessor,
            )
        ):
            from .exceptions import CircuitError

            raise CircuitError(
                "At least one of 'retval_none', 'retval', 'retval_in', or a 'retval_accessor' must be provided."
            )


@typechecked
@dataclass(frozen=True)
class ServicePolicy:
    """
    Configuration for how the circuit breaker treats failures for a particular service.

    Parameters
    ----------
    window_seconds:
        Time window (in seconds) during which failures are counted toward the
        `max_failures` limit.
    max_failures:
        Maximum allowed failures in the sliding window before the circuit is
        considered *open* for the associated service.
    ignore_exceptions:
        Iterable of exception *classes* which should **not** be recorded as failures.
        Example: ``(ValueError, )``. If an exception raised by the protected code is an
        instance of a class in this iterable, that exception will be ignored.
    on_exceptions:
        Iterable of exception *classes* which should **only** be recorded as failures.
        If provided, only exceptions matching this list will be recorded; all other
        exceptions will be ignored. This acts as an allow-list.
        Note: ``ignore_exceptions`` is checked first.
    on_retval_policy:
        Optional :class:`ReturnValuePolicy` used to classify successful return values
        as failures (for example, when a downstream service returns a sentinel value).
        If None, no return-value-based checks are applied.

    Notes
    -----
    - ``ignore_exceptions`` and ``on_exceptions`` accept exception **classes** (or tuples).
      Use subclasses to match broad categories.
    - If both ``ignore_exceptions`` and ``on_exceptions`` are provided, ``ignore_exceptions``
      takes precedence for matched exception types.
    - ``on_retval_policy`` only applies to *successful* calls (i.e., calls that did not
      raise): if the policy matches the returned value, the call will be treated as a
      failure (the breaker records a failure and a `ReturnValuePolicyError` is raised).
    """

    window_seconds: int
    max_failures: int
    ignore_exceptions: Iterable[type[BaseException]] | None = None
    on_exceptions: Iterable[type[BaseException]] | None = None
    on_retval_policy: Optional[ReturnValuePolicy] = None
