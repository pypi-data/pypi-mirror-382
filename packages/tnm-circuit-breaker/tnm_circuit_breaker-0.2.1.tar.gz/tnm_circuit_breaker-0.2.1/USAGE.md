# USAGE.md

Practical guides on how one might integrate **tnm-circuit-breaker** into common app types:
FastAPI, Celery tasks, and a CLI worker.

> Assumes you have already created a `CircuitBreaker` instance (singleton) at app startup and called `initialize()`.

---

## Four Ways to use the Circuit Breaker

The circuit breaker provides three ways to protect your code:

### a) The `protect` decorator

The `@breaker.protect("service-name")` decorator is the most common way to use the circuit breaker. It can be applied to
both synchronous and asynchronous functions.

```py
@breaker.protect("my-service")
def my_function():
    ...


@breaker.protect("my-async-service")
async def my_async_function():
    ...
```

### b) The `execute` method

The `breaker.execute("service-name", my_function)` method is useful for protecting code that is not defined with a
decorator. It is for synchronous functions.

```py
def my_function(): ...


breaker.execute("my-service", my_function)

```

### c) The `execute_async` method

The `breaker.execute_async("service-name", my_async_function)` method is the asynchronous equivalent of the `execute`
method. It is for coroutines or callables that return a coroutine.

```py
async def my_async_function(): ...


await breaker.execute_async("my-async-service", my_async_function)

```

### d) Manual circuit control

The `breaker.is_available("service-name")` method can be used to check if a service's circuit is open. This can be used
to implement custom circuit control logic.

```py
def my_function():
    try:
        ...
    except Exception as e:
        breaker.record_failure("my-service", str(e))
    else:
        breaker.record_success("my-service")

    my_function()

    # elsewhere
    if not breaker.is_available("my-service"):
        print("my-service is down due to: ", breaker.last_failure("my-service")["reason"])

```

---

## 1. Shared setup (create a single breaker instance)

Put this in a module that other parts of your app import (e.g. `myapp/breaker.py`).

```py
# myapp/breaker.py
from tnm.circuit import CircuitBreaker
from tnm.circuit.policies import ServicePolicy

default_policy = ServicePolicy(window_seconds=60 * 5, max_failures=10)
service_policies = {
    "elasticsearch": ServicePolicy(window_seconds=60 * 30, max_failures=10, ignore_exceptions=[BadRequestException]),
    "rabbitmq": ServicePolicy(window_seconds=60, max_failures=3),
    "kafka": ServicePolicy(window_seconds=60, max_failures=5),
    "postgres": ServicePolicy(window_seconds=60, max_failures=5),
    "external-http": ServicePolicy(window_seconds=30, max_failures=3, on_exceptions=[BadRequestException]),
}

# Use 'local' for single-process or 'redis' for distributed/clustered apps.
breaker = CircuitBreaker(
    backend="redis",  # or "local"
    default_policy=default_policy,
    service_policies=service_policies,
    # redis only:
    redis_url="redis://127.0.0.1:6379/0",
    namespace="myapp:circuit",
    meta_ttl_seconds=300,
)

# initialize at app startup
breaker.initialize()
```

or use the `tnm.circuit.get_breaker` facade:

```py
from tnm.circuit import get_breaker

breaker = get_breaker(
    # backend="redis",
    default_policy=default_policy,
    service_policies=service_policies,
    # **redis_kwargs
)  # already initialized, local backend
```

---

## Customization options

Both the `protect` decorator and the `execute` / `execute_async` methods accept the same per-call overrides:

* `failure_reason: str | None`
  Custom reason to record when a return-value policy triggers. If omitted a computed reason is used.

* `ignore_exceptions: Iterable[type[BaseException]] | None`
  Exceptions in this list will **not** be recorded as failures (they still propagate).

* `on_exceptions: Iterable[type[BaseException]] | None`
  If provided, **only** exceptions in this list are recorded as failures (exceptions not in the list are ignored for
  counting).

* `on_retval_policy: ReturnValuePolicy | None`
  Rich rule that determines whether certain return values should be treated as failures. See the next section.

**Precedence** when mixing overrides:

1. Per-call / per-decorator override (arguments to `protect(...)` or `execute(...)`).
2. Service-specific policy supplied to `CircuitBreaker`.
3. `default_policy` supplied to `CircuitBreaker`.

**Important:** The `protect(...)` decorator resolves effective policy overrides at *decoration time* (when the decorator
is applied). If you need per-call dynamic overrides, use `execute`/`execute_async` or create the decorated function
after adjusting the policy. `execute` and `execute_async` resolve overrides at *call time*.

## ReturnValuePolicy (treating return values as failures)

`ReturnValuePolicy` describes which return values should be treated as failures. Typical uses: HTTP clients that return
a response object, or client libs that return sentinel values instead of raising.

Key fields and behaviour:

* `retval_none: bool`
  If returned value is `None`, it is considered a failure when `retval_none` is `True`.

* `retval: Any`
  If return value matches this, it is considered a failure.

* `retval_in: Iterable[Any]`
  If return value is in this list, it is considered a failure.

* `retval_accessor: str | None`
  A dotted accessor applied to the result before evaluation (e.g. `"status_code"`, `"data.code"`, `"meta.get_code"`). If
  this accessor must accept `*args` or `**kwargs`, pass `retval_accessor_args: tuple` or `retval_accessor_kwargs: dict`.

When a return-value rule matches the call, the breaker will:

1. record a failure using a reason string, and
2. raise `ReturnValuePolicyError` (which contains `.retval` and `.retval_policy` so callers can react).

**Examples:**

```py
from tnm.circuit.policies import ReturnValuePolicy

# Treat HTTP status codes 500 and 502 as failures by accessing .status_code
policy = ReturnValuePolicy(retval_accessor="status_code", retval_in=[500, 502])

```

Use the policy:

```py
@breaker.protect("external-http", on_retval_policy=policy,
                 on_exceptions=[httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError])
async def call_external(...):
    return await httpx.client.get(...)


from tnm.circuit.exceptions import ReturnValuePolicyError

try:
    await call_external()
except ReturnValuePolicyError as e:
    # the function call returned an object with an accessor of 'status_code' that was in [500, 502]
    handle_degraded_mode()
except CircuitOpenError:
    # the function call raise the exceptions in on_exceptions and a failure was recorded.
    handle_degraded_mode()
except Exception as e:
    # the function call raise an exception that was not in on_exceptions
    handle_degraded_mode()
```

---

## 2. FastAPI example

* initialize on startup/shutdown
* dependency injection for the breaker

```py
# myapp/main.py
import asyncio
import logging
from datetime import datetime
from functools import partial

import httpx
from elasticsearch import Elasticsearch
from fastapi import FastAPI, Depends, HTTPException
from myapp.breaker import breaker  # singleton from above
from tnm.circuit.exceptions import CircuitOpenError, CircuitError

logger = logging.getLogger(__name__)


def app_lifespan():
    try:
        logger.info("Initializing circuit breaker")
        breaker.initialize()
        yield
    except CircuitError as e:
        logger.error(f"Failed to initialize circuit breaker: {e}")
    finally:
        logger.info("Shutting down circuit breaker")


app = FastAPI(
    title="MyApp",
    description="My App",
    lifespan=app_lifespan
)


@app.get("/search")
async def search(q: str):
    @breaker.protect("elasticsearch", on_exceptions=[ConnectionError])
    def _do_search():
        es = Elasticsearch()
        return es.search(index="my-index", body={"query": {"match": {"q": q}}})

    try:
        return _do_search()
    except CircuitOpenError:
        last_failure = breaker.last_failure("elasticsearch")
        reason = last_failure['reason']
        failed_at = datetime.fromtimestamp(last_failure['ts'])
        raise HTTPException(status_code=503, detail="Search temporarily unavailable")


@app.post("/sync-update")
async def sync_update(payload: dict):
    # Example: run synchronous code safely under the breaker by running in thread pool.
    def update_db(data):
        from myapp.db import blocking_update  # example
        return blocking_update(data)

    loop = asyncio.get_running_loop()
    try:
        return await breaker.execute_async("postgres", loop.run_in_executor(None, partial(update_db, payload)))
    except CircuitOpenError:
        raise HTTPException(status_code=503, detail="Database unavailable")
```

**Notes**

* You can use `@breaker.protect("service-name")` for both sync and async callables.
* `breaker.execute(...)` is for executing sync callables while `breaker.execute_async(...)` is for executing async
  callables.

---

## 4. Celery tasks example

Celery tasks are often synchronous (worker process). Protect them by checking `is_available()` before performing work
and recording failure/success manually inside the task.

```py
# tasks.py (Celery)
from celery import Celery
from myapp.breaker import breaker
from tnm.circuit import CircuitOpenError

celery = Celery(...)


@celery.task(bind=True, max_retries=3)
def publish_to_rabbit(self, payload):
    service = "rabbitmq"

    # Quick rejection if the circuit for rabbitmq is open
    if not breaker.is_available(service):
        # Either requeue with delay, or fail-fast with a graceful error
        raise self.retry(countdown=30, exc=Exception("RabbitMQ circuit open"))

    try:
        # actual publish logic (sync or wrappers around sync client)
        from myapp.messaging import publish  # implement your publisher
        publish(payload)
    except Exception as exc:
        # Record failure for the service (used to open the circuit)
        breaker.record_failure(service, str(exc))
        # re-raise to allow Celery retry policies to work
        raise
    else:
        # mark success (resets failure counts)
        breaker.record_success(service)
        return {"status": "ok"}
```

Alternative: use same `@breaker.protect("rabbitmq")` decorator on function.

---

## 5. CLI worker / one-off script

Small worker that consumes a queue or processes a file

```py
# worker.py
import time
from myapp.breaker import breaker
from tnm.circuit import CircuitOpenError


def process_item(item):
    # blocking work (DB insert, publish, etc.)
    pass


def main():
    breaker.initialize()  # ensure backend ready

    while True:
        item = get_next_item()  # implement reading from queue / filesystem
        try:
            # short-circuit if the downstream service is known to be unhealthy
            if not breaker.is_available("external-http"):
                print("Downstream service unhealthy — requeue or sleep")
                time.sleep(10)
                continue

            process_item(item)
            breaker.record_success("external-http")
        except Exception as exc:
            breaker.record_failure("external-http", str(exc))
            print("Failed to process item:", exc)
            # implement requeue/alert/backoff as needed


if __name__ == "__main__":
    main()
```

**Notes**

* CLI workers often run in a single process: prefer `backend="local"` for simplicity (or `redis` if many workers must
  share state).

---

## 5. Realistic integration patterns & fallbacks

### a) External HTTP API (payments, auth)

* If circuit opens: return cached response, use degraded mode, or offer user-friendly error (503).
* Always record failure reasons (short strings) to help ops debug.

### b) Message brokers (RabbitMQ / Kafka)

* For producers: if the broker is down, either buffer to disk / local queue, or drop with backpressure.
* For consumers: circuit breaker less useful for consuming (use partitioned retries), but still useful for protecting
  producer-side interactions.

### c) Postgres

* For transient DB outages, a conservative policy with lower `max_failures` and longer window can avoid flapping.
* Use `breaker.record_failure(...)` from exception handlers in DAOs and `record_success()` on successful commits.

---

## 6. Small checklist before production

* Call `breaker.initialize()` at app startup or use the `tnm.circuit.get_breaker` facade which is already initialized.
* Namespace Redis keys with `namespace="myapp:circuit"` if using shared Redis.
* Tune `ServicePolicy`: critical services should have stricter or looser thresholds depending on tolerance.
* Consider telemetry: record metrics for failures (`record_failure`) and openings (when `is_available` returns `False`).

