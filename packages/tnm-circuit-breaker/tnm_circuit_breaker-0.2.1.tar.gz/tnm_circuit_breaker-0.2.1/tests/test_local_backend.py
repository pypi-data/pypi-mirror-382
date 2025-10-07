import time


def test_sqlite_backend_basic(sqlite_backend):
    svc = "test-svc"
    ts_old = int(time.time() - 120)
    ts_new = int(time.time())
    cnt1 = sqlite_backend.record_failure(svc, "err-old", timestamp=ts_old)
    assert isinstance(cnt1, int) and cnt1 >= 1
    cnt2 = sqlite_backend.record_failure(svc, "err-now", timestamp=ts_new)
    assert isinstance(cnt2, int) and cnt2 >= 1

    cutoff_recent = int(time.time() - 60)
    cnt_after_cleanup = sqlite_backend.get_failure_count(svc, cutoff=cutoff_recent)
    assert cnt_after_cleanup == 1

    last = sqlite_backend.get_last_failure(svc)
    assert isinstance(last, dict)
    assert isinstance(last.get("ts"), int)

    sqlite_backend.record_success(svc)
    assert sqlite_backend.get_last_failure(svc) is None
    assert sqlite_backend.get_failure_count(svc, cutoff=int(time.time() - 3600)) == 0


def test_get_failure_count_expiry(sqlite_backend):
    svc = "expire-test"
    ts_old = int(time.time() - 3600)
    sqlite_backend.record_failure(svc, "old", timestamp=ts_old)

    cutoff = int(time.time() - 60)
    remaining = sqlite_backend.get_failure_count(svc, cutoff=cutoff)
    assert remaining == 0


def test_sqlite_persists_multiple_services(sqlite_backend):
    svc_a = "svcA"
    svc_b = "svcB"

    sqlite_backend.record_failure(svc_a, "a1")
    sqlite_backend.record_failure(svc_b, "b1")
    sqlite_backend.record_failure(svc_a, "a2")

    ca = sqlite_backend.get_failure_count(svc_a, cutoff=int(time.time() - 3600))
    cb = sqlite_backend.get_failure_count(svc_b, cutoff=int(time.time() - 3600))
    assert ca >= 1
    assert cb >= 1

    la = sqlite_backend.get_last_failure(svc_a)
    lb = sqlite_backend.get_last_failure(svc_b)
    assert la is not None and lb is not None
    assert la != lb
