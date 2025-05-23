import threading
from time import sleep
from typing import Union

from flipcache import ThreadSafeFIFODict

fd = ThreadSafeFIFODict(max_items=5)


def writer(prefix: str, delay: Union[int, float]):
    for i in range(4):
        key = f"{prefix}{i}"
        fd[key] = i
        print(f"[{prefix}] Set {key} = {i}")
        sleep(delay)


threads = [
    threading.Thread(target=writer, args=("A", 0.1)),
    threading.Thread(target=writer, args=("B", 0.15)),
]

for t in threads:
    t.start()
for t in threads:
    t.join()

print("\nFinal contents:")
for k, v in fd.items():
    print(f"{k}: {v}")
