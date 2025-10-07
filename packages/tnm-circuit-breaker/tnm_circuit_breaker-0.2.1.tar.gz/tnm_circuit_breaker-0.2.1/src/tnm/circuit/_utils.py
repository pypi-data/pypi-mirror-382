from __future__ import annotations

from typing import Literal

from ._breaker import CircuitBreaker
from ._typeguard import typechecked
from .policies import ServicePolicy


@typechecked
def get_breaker(
    backend: Literal["redis", "local"] = "local",
    default_policy: ServicePolicy | None = None,
    service_policies: dict[str, ServicePolicy] | None = None,
    **kwargs,
) -> CircuitBreaker:
    """
    Get a CircuitBreaker instance, configured and initialized.

    This function acts as a factory for creating CircuitBreaker instances.
    For Redis backend, connection arguments should be passed via kwargs.

    Parameters
    ----------
    backend : Literal["redis", "local"], optional
        The backend to use for storing circuit breaker state. Defaults to "local".
    default_policy : ServicePolicy | None, optional
        The default policy for services. If not provided, a default policy is created:
        ServicePolicy(window_seconds=1800, max_failures=15).
    service_policies : dict[str, ServicePolicy] | None, optional
        A dictionary of service-specific policies to override the default.
    **kwargs
        Additional keyword arguments passed to the CircuitBreaker constructor.
        This is particularly useful for configuring the Redis backend, e.g., `redis_url`.

    Returns
    -------
    CircuitBreaker
        An initialized CircuitBreaker instance.
    """

    if not default_policy:
        default_policy = ServicePolicy(window_seconds=30 * 60, max_failures=15)

    breaker = CircuitBreaker(
        backend=backend,
        default_policy=default_policy,
        service_policies=service_policies or {},
        **kwargs,
    )
    breaker.initialize()
    return breaker
