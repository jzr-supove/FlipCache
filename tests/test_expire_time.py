"""FX-1: expire_time accepts int, float, timedelta; et constants are ints."""
import datetime

import pytest

from flipcache import FlipCache, et


def public_constants():
    return {n: v for n, v in vars(et).items() if n.isupper()}


def test_et_has_constants():
    assert "FIFTEEN_MINUTES" in public_constants()


@pytest.mark.parametrize("name,value", sorted(public_constants().items()))
def test_every_et_constant_is_int(name, value):
    assert type(value) is int, f"{name}={value!r}"


def test_et_constant_values_unchanged():
    assert et.FIFTEEN_MINUTES == 900
    assert et.THIRTY_MINUTES == 1800
    assert et.HALF_AN_HOUR == 1800
    assert et.QUARTER_HOUR == 900


@pytest.mark.parametrize(
    "expire_time,expected",
    [
        (et.FIFTEEN_MINUTES, 900),
        (120, 120),
        (900.0, 900),
        (2.5, 3),
        (0.2, 1),
        (datetime.timedelta(minutes=2), 120),
        (datetime.timedelta(seconds=2, milliseconds=500), 3),
    ],
)
def test_write_sets_ttl_in_whole_seconds_rounded_up(redis_client, expire_time, expected):
    cache = FlipCache("x", expire_time=expire_time, redis_protocol=redis_client)
    cache["k"] = "v"
    assert redis_client.ttl("x:k") == expected


@pytest.mark.parametrize(
    "expire_time,expected",
    [(et.FIFTEEN_MINUTES, 900), (2.5, 3), (datetime.timedelta(seconds=90), 90)],
)
def test_refresh_method_sets_ttl_in_whole_seconds(redis_client, expire_time, expected):
    cache = FlipCache("x", expire_time=expire_time, redis_protocol=redis_client)
    cache["k"] = "v"
    redis_client.expire("x:k", 1)
    cache.refresh("k")
    assert redis_client.ttl("x:k") == expected


@pytest.mark.parametrize(
    "expire_time,expected",
    [(et.FIFTEEN_MINUTES, 900), (2.5, 3), (datetime.timedelta(seconds=90), 90)],
)
def test_refresh_on_get_after_local_miss_sets_ttl_in_whole_seconds(
    redis_client, expire_time, expected
):
    writer = FlipCache("x", expire_time=expire_time, redis_protocol=redis_client)
    writer["k"] = "v"
    redis_client.expire("x:k", 1)
    reader = FlipCache(
        "x", expire_time=expire_time, redis_protocol=redis_client,
        refresh_expire_time_on_get=True,
    )
    assert reader["k"] == "v"
    assert redis_client.ttl("x:k") == expected


def test_no_expire_time_keeps_key_without_ttl(redis_client):
    cache = FlipCache("x", expire_time=None, redis_protocol=redis_client)
    cache["k"] = "v"
    assert redis_client.ttl("x:k") == -1


def test_no_expire_time_refresh_does_not_add_ttl(redis_client):
    cache = FlipCache(
        "x", expire_time=None, redis_protocol=redis_client,
        refresh_expire_time_on_get=True,
    )
    cache["k"] = "v"
    cache.refresh("k")
    assert redis_client.ttl("x:k") == -1
