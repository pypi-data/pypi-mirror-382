from __future__ import annotations

import inspect
import time
from functools import cached_property
from typing import Literal, Callable, Any, Iterable, Union, Coroutine, Optional

from ._backends.sqlite_backend import SQLiteCircuitBackend
from ._helpers import (
    should_record_for_exception,
    should_record_for_returnval,
    inflect_str,
    effective_policy_overrides,
)
from ._typeguard import typechecked
from .exceptions import ReturnValuePolicyError, CircuitError, CircuitOpenError
from .interfaces import CircuitBackend
from .policies import ReturnValuePolicy, ServicePolicy


@typechecked
class CircuitBreaker:
    """
    Circuit breaker that coordinates failure tracking and availability checks.

    Parameters
    ----------
    backend : Literal["redis", "local"]
        Choose which backend to use. When set to `"local"`, a local backend will be used.
        When set to `"redis"`, the class expects Redis connection information in ``kwargs`` (see below).
    default_policy : ServicePolicy
        Fallback policy applied to any service that does not have an explicit entry in
        ``service_policies``.
    service_policies : dict[str, ServicePolicy] | None,
        Optional mapping of service-name -> `ServicePolicy` to override the default for
        specific services.
    **kwargs
        When ``backend == "redis"`` the following are recognized and required/expected:

        - ``redis_url`` (str) - Redis connection URL accepted by `redis.Redis` (e.g.
          ``"redis://localhost:6379/0"``).
        - ``namespace`` (str) - Optional key namespace for Redis keys. Defaults to
          ``"circuit"`` if not provided.
        - ``meta_ttl_seconds`` (int) - Optional TTL (in seconds) for per-service meta hashes.
            0 effectively keeps the meta forever. Defaults to 0.

    Raises
    ------
    CircuitError
        Raised for invalid configuration (for example, missing or invalid ``redis_url``),
        or when the selected backend cannot be connected to/initialized.
    CircuitBackendError
        Raised when the selected backend reports an operational error.
    CircuitOpenError
        Raised by the breaker decorators when callers attempt an operation while the circuit is open
    """

    scheme: str = "sliding-window"

    def __init__(
        self,
        backend: Literal["redis", "local"],
        default_policy: ServicePolicy,
        service_policies: dict[str, ServicePolicy] | None = None,
        **kwargs,
    ):
        self._storage_backend = backend.lower()
        self._default_policy = default_policy
        self._policies = service_policies or {}
        self._kwargs = kwargs

    @cached_property
    def _backend(self) -> CircuitBackend:
        if self._storage_backend == "local":
            return SQLiteCircuitBackend()

        try:
            from ._backends.redis_backend import RedisCircuitBackend
            from ._redis import RedisClient
        except (ImportError, ModuleNotFoundError) as e:
            raise CircuitError(
                "Redis support is not enabled. Install it with `pip install tnm-circuit[redis]`."
            ) from e

        reds_url = self._kwargs.get("redis_url", None)

        if not isinstance(reds_url, str):
            raise CircuitError(
                "Pass a string-backed 'redis_url' keyword argument to use the Redis backend."
            )

        client = RedisClient.get_client(reds_url)
        try:
            client.ping()
        except Exception as e:
            raise CircuitError("Failed to connect to Redis.") from e
        try:
            return RedisCircuitBackend(
                client,
                namespace=str(self._kwargs.get("namespace", "circuit")),
                meta_ttl_seconds=int(self._kwargs.get("meta_ttl_seconds", 0)),
            )
        except Exception as exc:
            raise CircuitError(
                f"Failed to initialize redis backend: {str(exc)}"
            ) from exc

    def policy_for(self, service: str) -> ServicePolicy:
        return self._policies.get(service, self._default_policy)

    def initialize(self):
        self._backend.initialize()

    def is_available(self, service: str) -> bool:
        policy = self.policy_for(service)
        cutoff = int(time.time() - policy.window_seconds)
        return (
            self._backend.get_failure_count(service, cutoff=cutoff)
            < policy.max_failures
        )

    def record_failure(
        self, service: str, reason: str, timestamp: float | None = None
    ) -> int:
        """Record a failure and return the new failure count in the window."""
        self._backend.record_failure(service, reason, timestamp)
        policy = self.policy_for(service)
        cutoff = int((timestamp or time.time()) - policy.window_seconds)
        return self._backend.get_failure_count(service, cutoff=cutoff)

    def last_failure(self, service: str):
        return self._backend.get_last_failure(service)

    def record_success(self, service: str, timestamp: float | None = None) -> None:
        self._backend.record_success(service, timestamp)

    def protect(
        self,
        service: str,
        *,
        failure_reason: str | None = None,
        ignore_exceptions: Iterable[type[BaseException]] | None = None,
        on_exceptions: Iterable[type[BaseException]] | None = None,
        on_retval_policy: Optional[ReturnValuePolicy] | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        protect a function with the circuit breaker.

        When the decorated function is called, the circuit breaker first checks if the
        service is available. If the circuit is open, it raises a :class:`~.exceptions.CircuitOpenError`.

        If the circuit is closed, the function is executed.

        - If the function raises an exception, the circuit breaker records a failure
          (unless the exception type is in ``ignore_exceptions``).
        - If the function returns a value that matches the ``on_retval_policy``, the
          circuit breaker records a failure.
        - Otherwise, the circuit breaker records a success.

        Parameters
        ----------
        service : str
            The name of the service to protect.
        failure_reason : str, optional
            A custom reason to record for failures.
        ignore_exceptions : Iterable[type[BaseException]], optional
            A list of exception types to ignore.
        on_exceptions : Iterable[type[BaseException]], optional
            A list of exception types to handle.
        on_retval_policy : ReturnValuePolicy, optional
            A policy for handling return values.

        Returns
        -------
        Callable
            The decorated function.
        """

        def _decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            is_async = inspect.iscoroutinefunction(func)

            ignore_tuple, onex_tuple, retval_policy = effective_policy_overrides(
                self,
                service,
                "merge",
                ignore_exceptions=ignore_exceptions,
                on_exceptions=on_exceptions,
                on_retval_policy=on_retval_policy,
            )

            if is_async:

                async def _wrapper(*args, **kwargs):
                    if not self.is_available(service):
                        self.raise_circuit_open_error(service)
                    try:
                        result = await func(*args, **kwargs)
                    except Exception as exc:
                        if should_record_for_exception(exc, ignore_tuple, onex_tuple):
                            reason = f"{type(exc).__name__}: {str(exc)}"
                            self.record_failure(service, reason)
                        raise
                    else:
                        return _should_record_for_returnval(retval_policy, result)

            else:

                def _wrapper(*args, **kwargs):
                    self.raise_circuit_open_error(service)
                    try:
                        result = func(*args, **kwargs)
                    except Exception as exc:
                        if should_record_for_exception(exc, ignore_tuple, onex_tuple):
                            reason = f"{type(exc).__name__}: {str(exc)}"
                            self.record_failure(service, reason)
                        raise
                    else:
                        return _should_record_for_returnval(retval_policy, result)

            _wrapper.__name__ = getattr(func, "__name__", "protected_fn")
            _wrapper.__doc__ = getattr(func, "__doc__", "")
            return _wrapper

        def _should_record_for_returnval(retval_policy, result):
            rc = should_record_for_returnval(retval_policy, result)
            if rc:
                _, reason = rc
                self.record_failure(service, reason)
                raise ReturnValuePolicyError(
                    f"A failure was recorded for service '{service}' because the return value "
                    f"'{result}' triggered the return value policy: {failure_reason or reason}",
                    retval=result,
                    retval_policy=retval_policy,
                )
            self.record_success(service)
            return result

        return _decorator

    def execute(
        self,
        service: str,
        func: Callable[[], Any],
        *,
        failure_reason: str | None = None,
        ignore_exceptions: Iterable[type[BaseException]] | None = None,
        on_exceptions: Iterable[type[BaseException]] | None = None,
        on_retval_policy: Optional[ReturnValuePolicy] = None,
    ) -> Any:
        """
        Executes a function under circuit protection (sync).

        This method is a convenience wrapper around the :meth:`protect` decorator.
        It is useful for calling functions that are not decorated.

        Parameters
        ----------
        service : str
            The name of the service to protect.
        func : Callable[[], Any]
            The function to execute.
        failure_reason : str, optional
            A custom reason to record for failures.
        ignore_exceptions : Iterable[type[BaseException]], optional
            A list of exception types to ignore.
        on_exceptions : Iterable[type[BaseException]], optional
            A list of exception types to handle.
        on_retval_policy : ReturnValuePolicy, optional
            A policy for handling return values.

        Returns
        -------
        Any
            The result of the function.
        """
        self.raise_circuit_open_error(service)

        ignore_tuple, onex_tuple, retval_policy = effective_policy_overrides(
            self,
            service,
            "merge",
            ignore_exceptions=ignore_exceptions,
            on_exceptions=on_exceptions,
            on_retval_policy=on_retval_policy,
        )

        try:
            result = func()
        except Exception as exc:
            if should_record_for_exception(exc, ignore_tuple, onex_tuple):
                reason = failure_reason or f"{type(exc).__name__}: {str(exc)}"
                self.record_failure(service, reason)
            raise
        else:
            rc = should_record_for_returnval(retval_policy, result)
            if rc:
                _, reason = rc
                self.record_failure(service, reason)
                raise ReturnValuePolicyError(
                    f"A failure was recorded for service '{service}' because the return value "
                    f"'{result}' triggered the return value policy: {reason}",
                    retval=result,
                    retval_policy=retval_policy,
                )
            self.record_success(service)
            return result

    async def execute_async(
        self,
        service: str,
        coro_or_callable: Union[
            Callable[[], Coroutine[Any, Any, Any]], Coroutine[Any, Any, Any]
        ],
        *,
        failure_reason: str | None = None,
        ignore_exceptions: Iterable[type[BaseException]] | None = None,
        on_exceptions: Iterable[type[BaseException]] | None = None,
        on_retval_policy: Optional[ReturnValuePolicy] = None,
    ) -> Any:
        """
        Executes a coroutine under circuit protection (async).

        This method is a convenience wrapper around the :meth:`protect` decorator.
        It is useful for calling coroutines that are not decorated.

        Parameters
        ----------
        service : str
            The name of the service to protect.
        coro_or_callable : Union[Callable[[], Coroutine[Any, Any, Any]], Coroutine[Any, Any, Any]]
            The coroutine or callable to execute.
        failure_reason : str, optional
            A custom reason to record for failures.
        ignore_exceptions : Iterable[type[BaseException]], optional
            A list of exception types to ignore.
        on_exceptions : Iterable[type[BaseException]], optional
            A list of exception types to handle.
        on_retval_policy : ReturnValuePolicy, optional
            A policy for handling return values.

        Returns
        -------
        Any
            The result of the coroutine.
        """
        self.raise_circuit_open_error(service)

        ignore_tuple, onex_tuple, retval_policy = effective_policy_overrides(
            self,
            service,
            "merge",
            ignore_exceptions=ignore_exceptions,
            on_exceptions=on_exceptions,
            on_retval_policy=on_retval_policy,
        )

        try:
            if inspect.iscoroutine(coro_or_callable):
                result = await coro_or_callable
            elif callable(coro_or_callable):
                result = await coro_or_callable()
            else:
                raise TypeError(
                    "Expected a coroutine or a callable that returns a coroutine"
                )
        except Exception as exc:
            if should_record_for_exception(exc, ignore_tuple, onex_tuple):
                reason = failure_reason or f"{type(exc).__name__}: {str(exc)}"
                self.record_failure(service, reason)
            raise
        else:
            rc = should_record_for_returnval(retval_policy, result)
            if rc:
                _, reason = rc
                self.record_failure(service, reason)
                raise ReturnValuePolicyError(
                    f"A failure was recorded for service '{service}' because the return value "
                    f"'{result}' triggered the return value policy: {reason}",
                    retval=result,
                    retval_policy=retval_policy,
                )
            self.record_success(service)
            return result

    def raise_circuit_open_error(
        self, service: str, check_available: bool = True
    ) -> None:
        if not check_available:
            raise CircuitOpenError(f"circuit is open for service '{service}'")

        pol = self.policy_for(service)

        if not self.is_available(service):
            raise CircuitOpenError(
                "circuit is open for service '{service}' due to {f_count} within {window}".format(
                    service=service,
                    f_count=inflect_str(
                        item="failure",
                        count=self._backend.get_failure_count(
                            service,
                            int(time.time() - pol.window_seconds),
                        ),
                        include_count=True,
                    ),
                    window=inflect_str("second", pol.window_seconds, True),
                )
            )
