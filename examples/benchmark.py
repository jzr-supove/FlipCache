import statistics
import timeit
from redis import Redis
from flipcache import FlipCache

kp = "my_cache"
KEYS = 1_000

rdp = Redis(decode_responses=True)
cache = FlipCache(name="my_cache", redis_protocol=rdp, local_max=KEYS)


def redis_set():
    for i in range(KEYS):
        rdp.set(f"my_cache:{i}", i * 2)


def redis_get():
    for _ in range(100):
        for i in range(KEYS):
            v = rdp.get(f"my_cache:{i}")


def pycache_set():
    for i in range(KEYS):
        cache[i] = i * 2


def pycache_get():
    for _ in range(100):
        for i in range(KEYS):
            v = cache[i]


def benchmark(func):
    print("==============")
    print("Benchmark function:", func.__name__)
    times = timeit.repeat(func, number=1, repeat=5)
    mean_time = statistics.mean(times)
    std_dev = statistics.stdev(times)
    print(f"Mean execution time: {mean_time:.6f} seconds")
    print(f"Standard deviation: {std_dev:.6f} seconds")
    print("==============")


if __name__ == "__main__":
    benchmark(redis_set)
    benchmark(pycache_set)

    benchmark(redis_get)
    benchmark(pycache_get)
