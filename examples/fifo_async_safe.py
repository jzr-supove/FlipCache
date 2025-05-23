import asyncio
from flipcache import AsyncSafeFIFODict

fd = AsyncSafeFIFODict(max_items=5)


async def writer(name, delay):
    for i in range(4):
        key = f"{name}{i}"
        await fd.aset(key, i)
        print(f"[{name}] Set {key} = {i}")
        await asyncio.sleep(delay)


async def reader(name, delay):
    for _ in range(4):
        keys = await fd.akeys()
        print(f"[{name}] Current keys: {keys}")
        await asyncio.sleep(delay)


async def main():
    writers = [writer("X", 0.1), writer("Y", 0.15)]
    readers = [reader("R1", 0.2), reader("R2", 0.25)]
    await asyncio.gather(*writers, *readers)

    print("\nFinal contents:")
    for k, v in await fd.aitems():
        print(f"{k}: {v}")


asyncio.run(main())
