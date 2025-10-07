# tnm-circuit-breaker

A lightweight Python circuit breaker for protecting downstream systems.

> See **[USAGE](https://github.com/tnm-circuit-breaker/USAGE.md)** for full examples.

---

## Quick summary

* Purpose: protect downstream services (i.e., Elasticsearch, RabbitMQ, Kafka, Postgres, external HTTP APIs, ...) from
  cascading failures.
* Backends:

    * `local`: no extra dependencies needed
    * `redis`: distributed backend using Redis for atomic operations.

---

## Install

```bash
# core package
pip install tnm-circuit-breaker

# redis support
pip install "tnm-circuit-breaker[redis]"

```

---

## `CircuitBreaker` Public APIs

```python
class CircuitBreaker:
    def record_failure(*args) -> int: ...

    def last_failure(*args): ...

    def record_success(*args) -> None: ...

    def protect(*args): ...

    # a decorator

    def execute(*args): ...

    async def execute_async(*args): ...

    def raise_circuit_open_error(*args): ...

```

---

## Quick Usage

### Using the `protect` decorator

```py
from tnm.circuit import get_breaker
from tnm.circuit.exceptions import CircuitOpenError

breaker = get_breaker()  # defaults


@breaker.protect("service-name")
def my_function():
    pass


try:
    my_function()
except CircuitOpenError:
    ...
    # handle circuit open
```

### Using the `execute` method

```py
from tnm.circuit import get_breaker
from tnm.circuit.exceptions import CircuitOpenError

breaker = get_breaker()  # defaults


def my_function():
    pass


try:
    breaker.execute("service-name", my_function)
except CircuitOpenError:
    ...
    # handle circuit open
```

### Using the `execute_async` method

```py
import asyncio
from tnm.circuit import get_breaker
from tnm.circuit.exceptions import CircuitOpenError

breaker = get_breaker()  # defaults


async def my_async_function():
    pass


async def main():
    try:
        await breaker.execute_async("service-name", my_async_function)
    except CircuitOpenError:
        ...
        # handle circuit open


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Exceptions

All library exceptions inherit from a small, focused hierarchy:

* `CircuitError`: Base exception for all circuit breaker errors.
* `CircuitBackendError`: backend operational issues.
* `CircuitOpenError`: raised when an operation is attempted while a service's circuit is open.
* `ReturnValuePolicyError`: raised when a return-value rule matched; contains `.retval` and `.retval_policy`.

Handle `CircuitOpenError` or `ReturnValuePolicyError` as an expected operational outcome.

When catching, inspect `.args` or `.__cause__` for low-level detail.

---

## Contributing

Contributions welcome.

---

## License

MIT
