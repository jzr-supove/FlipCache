import asyncio
import random

from flipcache import AsyncSafeLRUDict

ld = AsyncSafeLRUDict(max_items=4)


async def writer(name, delay):
    for i in range(6):
        key = f"{name}{i}"
        await ld.aset(key, i)
        print(f"[{name}] Set {key} = {i}")
        await asyncio.sleep(delay)


async def reader(name, delay):
    for _ in range(5):
        keys = await ld.akeys()
        rand_key = random.choice(keys)
        rand_value = await ld.aget(rand_key)
        print(f"[{name}] Get {rand_key}:{rand_value}")

        keys = await ld.akeys()
        print(f"[{name}] Keys: {keys}")
        await asyncio.sleep(delay)


async def main():
    writers = [writer("X", 0.1), writer("Y", 0.12)]
    readers = [reader("R1", 0.15), reader("R2", 0.18)]

    await asyncio.gather(*writers, *readers)

    print("\nFinal keys:", await ld.akeys())


asyncio.run(main())
