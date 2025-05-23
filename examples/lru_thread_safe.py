import threading
from flipcache import ThreadSafeLRUDict
from time import sleep

ld = ThreadSafeLRUDict(max_items=4)


def writer(name, delay):
    for i in range(5):
        key = f"{name}{i}"
        ld[key] = i
        print(f"[{name}] Set {key} = {i}")
        sleep(delay)


def reader(name, delay):
    for _ in range(5):
        keys = list(ld.keys())
        print(f"[{name}] Keys: {keys}")
        sleep(delay)


threads = [
    threading.Thread(target=writer, args=("W1", 0.1)),
    threading.Thread(target=writer, args=("W2", 0.15)),
    threading.Thread(target=reader, args=("R1", 0.12)),
]

for t in threads:
    t.start()

for t in threads:
    t.join()

print("\nFinal keys:", list(ld.keys()))
