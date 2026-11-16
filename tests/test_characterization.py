"""Current, working behaviour the articles describe; must not regress."""
from flipcache import FlipCache


def test_local_hit_makes_no_redis_call(redis_client):
    cache = FlipCache("x", redis_protocol=redis_client)
    cache["k"] = "v"
    redis_client.calls.clear()
    assert cache["k"] == "v"
    assert redis_client.calls == []


def test_local_miss_rehydrates_from_redis(redis_client):
    redis_client.set("x:k", "from-redis")
    cache = FlipCache("x", redis_protocol=redis_client)
    assert "k" not in cache.local
    assert cache["k"] == "from-redis"
    assert cache.local["k"] == "from-redis"
    redis_client.calls.clear()
    assert cache["k"] == "from-redis"
    assert redis_client.calls == []


def test_local_max_evicts_oldest(redis_client):
    cache = FlipCache("x", local_max=2, redis_protocol=redis_client)
    cache["a"], cache["b"], cache["c"] = "1", "2", "3"
    assert list(cache.local) == ["b", "c"]
    assert cache["a"] == "1"  # still served from Redis
    assert redis_client.get("x:a") == "1"


def test_json_round_trip_through_redis(redis_client):
    data = {"a": [1, 2], "b": None}
    FlipCache("x", value_type="json", redis_protocol=redis_client)["k"] = data
    assert redis_client.get("x:k") == '{"a": [1, 2], "b": null}'
    assert FlipCache("x", value_type="json", redis_protocol=redis_client)["k"] == data


def test_int_round_trip_through_redis(redis_client):
    FlipCache("x", value_type="int", redis_protocol=redis_client)["k"] = 42
    value = FlipCache("x", value_type="int", redis_protocol=redis_client)["k"]
    assert value == 42 and isinstance(value, int)


def test_value_default_is_returned_and_written_back(redis_client):
    cache = FlipCache("x", value_default="dflt", redis_protocol=redis_client)
    assert cache["missing"] == "dflt"
    assert redis_client.get("x:missing") == "dflt"
    assert cache.local["missing"] == "dflt"


def test_missing_key_without_default_returns_none(redis_client):
    cache = FlipCache("x", redis_protocol=redis_client)
    assert cache["nope"] is None
    assert redis_client.exists("x:nope") == 0


def test_delete_removes_from_both_tiers(redis_client):
    cache = FlipCache("x", redis_protocol=redis_client)
    cache["k"] = "v"
    del cache["k"]
    assert "k" not in cache.local
    assert redis_client.exists("x:k") == 0
