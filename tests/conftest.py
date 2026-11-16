import fakeredis
import pytest


class SpyRedis(fakeredis.FakeRedis):
    """FakeRedis that records every command sent to the server."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calls = []

    def execute_command(self, *args, **kwargs):
        self.calls.append(str(args[0]).upper())
        return super().execute_command(*args, **kwargs)


@pytest.fixture
def redis_client():
    return SpyRedis(server=fakeredis.FakeServer(), decode_responses=True)


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def monotonic(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@pytest.fixture
def clock(monkeypatch):
    """Clock seam: flipcache.flipcache must `import time` and call `time.monotonic()`.

    The module-level name `time` is replaced with a fake exposing only `monotonic`.
    """
    import flipcache.flipcache as module

    fake = FakeClock()
    monkeypatch.setattr(module, "time", fake, raising=False)
    return fake
