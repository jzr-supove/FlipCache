"""value_default must not be shared between keys (FX-6)."""

from flipcache import FlipCache


def make(redis_client, **kw):
    return FlipCache("defaults", value_type="json", redis_protocol=redis_client, **kw)


def test_mutating_one_keys_default_does_not_change_another_keys(redis_client):
    cache = make(redis_client, value_default={"hits": 0})
    first = cache["u1"]
    first["hits"] += 1
    cache["u1"] = first

    assert cache["u2"] == {"hits": 0}
    assert cache["u1"] == {"hits": 1}


def test_mutating_a_returned_default_without_writing_back_leaves_the_default(redis_client):
    cache = make(redis_client, value_default={"tags": []})
    cache["u1"]["tags"].append("x")

    assert cache["u2"] == {"tags": []}


def test_default_is_still_written_back_to_both_tiers(redis_client):
    cache = make(redis_client, value_default={"hits": 0})
    assert cache["u1"] == {"hits": 0}
    assert "u1" in cache.local
    assert redis_client.get("defaults:u1") == '{"hits": 0}'
