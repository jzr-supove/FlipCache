import time
from flipcache import FlipCache


"""
Initializing FlipCache for using it as expiring cache
- local_max = 0 
- expire_time = 5
"""


expiring = FlipCache("expiring", local_max=0, expire_time=2)
refreshing = FlipCache(
    "refreshing", local_max=0, expire_time=2, refresh_expire_time_on_get=True
)


def showcase():
    expiring["first"] = "Hello World!"
    time.sleep(1)
    print(expiring["first"])
    expiring["second"] = "Python"
    time.sleep(1)

    print(expiring["first"])  # None
    print(expiring["second"])  # Python
    print(len(expiring))  # 1

    # Now, do the same actions on `refreshing` cache
    refreshing["first"] = "Hello, World!"
    time.sleep(1)
    # Here redis key expire time refreshes when we access the key
    print(refreshing["first"])
    refreshing["second"] = "Python"
    time.sleep(1)

    print(refreshing["first"])  # Hello World!
    print(refreshing["second"])  # Python
    print(len(refreshing))  # 2


if __name__ == "__main__":
    showcase()
