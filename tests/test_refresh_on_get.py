"""FX-2: local hits refresh the Redis TTL at most once per key per T/2."""
from flipcache import FlipCache

T = 100


def make(redis_client, **kw):
    kw.setdefault("expire_time", T)
    kw.setdefault("refresh_expire_time_on_get", True)
    return FlipCache("x", redis_protocol=redis_client, **kw)


def test_local_hit_after_half_ttl_resets_redis_ttl(redis_client, clock):
    cache = make(redis_client)
    cache["k"] = "v"
    redis_client.expire("x:k", 10)  # stand-in for T-10 seconds having elapsed in Redis
    clock.advance(T / 2 + 1)
    assert cache["k"] == "v"
    assert redis_client.ttl("x:k") == T


def test_local_hits_before_half_ttl_issue_no_redis_command(redis_client, clock):
    cache = make(redis_client)
    cache["k"] = "v"
    redis_client.calls.clear()
    for _ in range(5):
        clock.advance(T / 2 / 6)
        assert cache["k"] == "v"
    assert redis_client.calls == []


def test_refresh_is_throttled_after_a_refresh(redis_client, clock):
    cache = make(redis_client)
    cache["k"] = "v"
    clock.advance(T / 2 + 1)
    redis_client.calls.clear()
    cache["k"]  # refreshes
    assert redis_client.calls.count("EXPIRE") == 1
    redis_client.calls.clear()
    clock.advance(T / 4)
    cache["k"]  # within T/2 of last refresh
    assert redis_client.calls == []
    clock.advance(T / 4 + 1)
    cache["k"]  # more than T/2 since last refresh
    assert redis_client.calls.count("EXPIRE") == 1


def test_throttle_is_tracked_per_key(redis_client, clock):
    cache = make(redis_client)
    cache["a"] = 1
    clock.advance(T / 2 + 1)
    cache["b"] = 2  # written just now
    redis_client.calls.clear()
    cache["b"]
    assert redis_client.calls == []
    cache["a"]
    assert redis_client.calls.count("EXPIRE") == 1


def test_rewrite_restarts_the_refresh_window(redis_client, clock):
    cache = make(redis_client)
    cache["k"] = "v"
    clock.advance(T / 2 + 1)
    cache["k"] = "v2"
    redis_client.calls.clear()
    assert cache["k"] == "v2"
    assert redis_client.calls == []


def test_continuously_read_key_gets_ttl_extended_repeatedly(redis_client, clock):
    cache = make(redis_client)
    cache["k"] = "v"
    refreshes = 0
    for _ in range(10):  # read every 0.6*T/2 for 3 TTLs worth of time
        clock.advance(T * 0.3)
        redis_client.calls.clear()
        assert cache["k"] == "v"
        refreshes += redis_client.calls.count("EXPIRE")
    assert refreshes >= 3


def test_refresh_off_local_hits_never_touch_redis(redis_client, clock):
    cache = make(redis_client, refresh_expire_time_on_get=False)
    cache["k"] = "v"
    redis_client.calls.clear()
    for _ in range(3):
        clock.advance(T * 10)
        assert cache["k"] == "v"
    assert redis_client.calls == []


def test_no_expire_time_local_hits_never_touch_redis(redis_client, clock):
    cache = make(redis_client, expire_time=None)
    cache["k"] = "v"
    redis_client.calls.clear()
    clock.advance(10_000)
    cache["k"]
    assert redis_client.calls == []


def test_miss_then_rehydrate_still_refreshes(redis_client, clock):
    make(redis_client)["k"] = "v"
    redis_client.expire("x:k", 10)
    fresh = make(redis_client)
    assert fresh["k"] == "v"
    assert redis_client.ttl("x:k") == T


def test_miss_rehydrate_refresh_off_does_not_refresh(redis_client, clock):
    make(redis_client)["k"] = "v"
    redis_client.expire("x:k", 10)
    fresh = make(redis_client, refresh_expire_time_on_get=False)
    assert fresh["k"] == "v"
    assert redis_client.ttl("x:k") == 10
