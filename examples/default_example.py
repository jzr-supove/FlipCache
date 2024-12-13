from flipcache import FlipCache

"""
Initializing FlipCache with default values
- local_max = 100
- expire_time = None
- key_type = str
- value_type = str
- value_default = None
"""

cache = FlipCache("test")


def showcase():
    # Even though key_type and value_type are str, any type can be passed, it will be converted to string automatically
    # Raises ValueError on failure to convert to string

    cache["hello"] = "world"
    cache["foo"] = "bar"
    cache["abra"] = "cadabra"
    cache[123] = 456

    for i in range(100):
        cache[i] = i * 2

    # Since local_max is 100, oldest keys will be gone from local memory when we exceed the 100 items
    # However, they still exist in redis and can be retrieved
    # In our case keys "hello", "foo", "abra" and "123" are dropped of from 'fast' memory

    # On local memory, all values are stored as is, value_type doesn't affect them
    # When they get accessed when they were removed from local memory, they will be returned in value_type type from redis
    # In our case, cache["2"] will return value 4 of type <int>, but cache[123] will return value 456 of type <str>
    #   since it was gone from local memory and retrieved from redis

    print(cache["2"], type(cache["2"]))  # 4 <class 'int'>
    print(cache["123"], type(cache["123"]))  # 456 <class 'str'>

    # While not right, technically you can pass a key of any type when key_type is set to str if the type can be
    # converted to str. Same with the value when value_type is set to str.
    # The thing to keep in mind is that, value gets converted to str when it gets retrieved from redis

    my_key = (1, 2)
    cache[my_key] = my_key
    print(cache[my_key], type(cache[my_key]))  # (1, 2) <class 'tuple'>

    # If you want to store custom data types, it's recommended to set value_type to 'custom' and specify
    # value_encoder and value_decoder functions

    # DELETION
    print(cache["hello"])  # world
    del cache["hello"]
    print(cache["hello"])  # None

    del cache["unknown"]  # Not raises error, when you try to delete not existing key

    # MEMBERSHIP CHECK
    print("hello" in cache)  # False
    print(123 in cache)  # True

    # ITERATE OVER KEYS

    # By default, it will iterate over redis store
    # Note: insertion order is not preserved when retrieving from redis
    for key in cache:
        print(key)

    # In order to iterate over local memory keys you need to do:
    # Note: insertion/access order is preserved, but you only iterate over local_max items
    for key in cache.local:
        print(key)

    # GETTING SIZE
    # By default, it calculates the length using redis
    print(len(cache))

    # In order to calculate count of elements in local memory, you can do:
    print(len(cache.local))

    # REFRESH


if __name__ == "__main__":
    showcase()
