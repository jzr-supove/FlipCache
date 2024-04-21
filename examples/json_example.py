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
