# ⚡️ FlipCache

[![Downloads total](https://pepy.tech/badge/flipcache)](https://pepy.tech/project/flipcache)
[![Downloads monthly](https://img.shields.io/pypi/dm/flipcache.svg)](https://pypi.python.org/pypi/flipcache)
[![PyPi Package Version](https://img.shields.io/pypi/v/flipcache.svg)](https://pypi.python.org/pypi/flipcache)
[![PyPi status](https://img.shields.io/pypi/status/flipcache.svg)](https://pypi.python.org/pypi/flipcache)
[![Supported python versions](https://img.shields.io/pypi/pyversions/flipcache.svg)](https://pypi.python.org/pypi/flipcache)
[![Github issues](https://img.shields.io/github/issues/goodeejay/flipcache.svg)](https://github.com/goodeejay/flipcache/issues)
[![MIT License](https://img.shields.io/pypi/l/flipcache.svg)](https://opensource.org/licenses/MIT)
![Views](https://komarev.com/ghpvc/?username=flipcache&label=views)

<img style="z-index:-1; float:right" src="assets/logo.jpg" alt="PyCache Logo" height="250px" width="auto">

Redis-backed hybrid caching for lightning-fast Python data access

### 🤷‍♂️ Why FlipCache?

- Seamlessly integrate Redis for accelerated data retrieval in your Python projects.
- Optimize performance with an in-memory cache layer backed by Redis persistence.
- Enjoy ease-of-use and flexible configuration

<br/>

## 📥 Installation
```bash
pip install flipcache
```

## 🚀 Key Features
- **Hybrid Caching**: Transparent in-memory caching combined with Redis for scalable persistence.
- **Expire Times**: Set custom expiration times for cached data.
- **Configurable**: Tailor cache size, data types, and more.

## 👨‍💻 Usage Examples
### Basic

```python
from flipcache import FlipCache

cache = FlipCache("my_cache")

cache["my_key"] = "my_value"
print(cache["my_key"])  # Outputs: "my_value"
print(cache["unknown"])  # Outputs: None
print("my_key" in cache)  # Outputs: True

```
Pros compared to using simple dictionary: 
- Data persistence backed by Redis
- Seamless data conversion from Redis to Python
- Fast data access, compared to pure redis
- Returns None instead of raising an error on key indexing

### Expiring Cache

```python
import time
from flipcache import FlipCache

expiring_cache = FlipCache("expiring", local_max=0, expire_time=5)

expiring_cache["data"] = "This will expire"
time.sleep(6)
print(expiring_cache["data"])  # Outputs: None
```
In order to expiring-feature work with its full potential, we need to set `local_max` to `0`, removing the caching layer. 
You lose out on faster data retrieval, in order to get precise expiration results.
We can combine `expire_time` and `local_max`, in that case we can access data from cache memory that could have been expired.

### JSON Cache

```python
from flipcache import FlipCache, et

user_data = FlipCache(
    "user_data",
    local_max=100,
    expire_time=et.THREE_DAYS,
    value_type="json"
)

data = {
    "state": 1,
    "orders": [1, 2, 3, 4],
    "items": {
        "foo": 1,
        "bar": True,
        "baz": []
    }
}

# Store data
user_data["some-uuid"] = data
print(user_data["some-uuid"])  # {'state': 1, 'orders': [1, 2, 3, 4], 'items': {'foo': 1, 'bar': True, 'baz': []}}

# Update data
data["state"] = 2
data["items"]["bar"] = False
user_data["some-uuid"] = data
print(user_data["some-uuid"])  # {'state': 2, 'orders': [1, 2, 3, 4], 'items': {'foo': 1, 'bar': False, 'baz': []}}

# Delete data
del user_data["some-uuid"]
print(user_data["some-uuid"])  # None
```

### Custom Encoder/Decoder

```python
from flipcache import FlipCache
from dataclasses import dataclass, field


@dataclass
class Shape:
    name: str = "default"
    dimensions: list[float] = field(default_factory=list)
    edges: int = 0
    area: float = 0

    def __post_init__(self):
        if not self.area and self.dimensions:
            self.area = self.dimensions[0] * self.dimensions[1]


def encode_shape(shape: Shape) -> str:
    return f"{shape.name}||{shape.dimensions}||{shape.edges}||{shape.area}"


def decode_shape(shape: str) -> Shape:
    data = shape.split("||")
    return Shape(
        name=data[0],
        dimensions=[float(num) for num in data[1].strip('[]').split(',') if num],
        edges=int(data[2]),
        area=float(data[3])
    )


my_shape = Shape(name='womp', dimensions=[4.1, 3.4], edges=6, area=16.38)
shape2 = Shape(name='wat', dimensions=[11, 22])

custom = FlipCache(
    "custom",
    local_max=0,
    key_type='int',
    value_type='custom',
    value_default=Shape(),
    value_encoder=encode_shape,
    value_decoder=decode_shape
)

custom[123] = my_shape
custom[456] = shape2
print(custom[123])  # Shape(name='womp', dimensions=[4.1, 3.4], edges=6, area=16.38)
print(custom[321])  # Shape(name='default', dimensions=[], edges=0, area=0.0)
print(custom[456])  # Shape(name='wat', dimensions=[11.0, 22.0], edges=0, area=242.0)
```

### FIFODict Example (First-In, First-Out)

```python
from flipcache import FIFODict

cache = FIFODict(max_items=3)

cache["a"] = "Apple"
cache["b"] = "Banana"
cache["c"] = "Cherry"

print(list(cache.keys()))  # ['a', 'b', 'c']

cache["d"] = "Date"  # Evicts 'a' (oldest)

print(list(cache.keys()))  # ['b', 'c', 'd']
```
✅ Items are evicted in the order they were inserted.

### LRUDict Example (Least Recently Used)

```python
from flipcache import LRUDict

cache = LRUDict(max_items=3)

cache["a"] = "Alpha"
cache["b"] = "Beta"
cache["c"] = "Gamma"
_ = cache["a"]  # Access 'a', making it most recently used

cache["d"] = "Delta"  # Evicts 'b' (least recently used)

print(list(cache.keys()))  # ['c', 'a', 'd']
```
✅ Accessing a key moves it to the end (most recently used).


For more usage examples and details, see [examples](./examples)

## ⚙️ Configuration Options
### FlipCache
- `local_max`: Maximum items in the in-memory cache.
- `expire_time`: Redis key expiration time.
- `key_type`: Expected key data type.
- `value_type`: Expected value data type.
- `value_encoder`: Custom function used to encode the value for redis
- `value_decoder`: Custom function used to decode the value from redis
- `refresh_expire_time_on_get`: Refresh Redis key expiration on access
- `redis_protocol`: custom redis.Redis instance to be passed

### FIFODict and LRUDict
- `max_items`: Maximum number of items the dict can hold (defaults 1000)


## 📊 Benchmarks

<details>
    <summary>Setup</summary>

```python
from flipcache import FlipCache
from redis import Redis

KEYS = 1_000
rdp = Redis(decode_responses=True)
cache = FlipCache(name="my_cache", redis_protocol=rdp, local_max=KEYS)


def redis_set():
    for i in range(KEYS):
        rdp.set(f"my_cache:{i}", i * 2)


def pycache_set():
    for i in range(KEYS):
        cache[i] = i * 2


def redis_get():
    for _ in range(100):
        for i in range(KEYS):
            v = rdp.get(f"my_cache:{i}")


def pycache_get():
    for _ in range(100):
        for i in range(KEYS):
            v = cache[i]
```
</details>

| Benchmark Name | Mean Time (s) | Standard Deviation |
|----------------|---------------|--------------------|
| redis_set      | 0.252         | 0.013              |
| flipcache_set  | 0.242         | 0.003              |
| redis_get      | 22.986        | 0.518              |
| flipcache_get  | 0.0172        | 0.000              |



## 📋 Plans for future releases
- Make it possible to use other redis implementations such as aioredis
- Create readthedocs site for detailed documentation
- Optimize and add new functionality
- Make it threadsafe
- Add tests
