import asyncio
import threading
from collections import OrderedDict


class FIFODict(OrderedDict):
    """
    A fixed-capacity FIFO (First-In, First-Out) dictionary.

    Stores key-value pairs up to a maximum number of items. When the limit is exceeded,
    the oldest inserted item is evicted.

    This class inherits from `OrderedDict` to maintain insertion order and manage eviction.

    Parameters:
        max_items (int): The maximum number of items to store.
    """

    def __init__(self, max_items=1000, *args, **kwargs):
        self._max_items = max_items
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        """
        Insert or update a key-value pair.

        If the key already exists, it is re-inserted at the end (treated as new).
        If the dictionary exceeds its max capacity, the oldest item is evicted.

        Parameters:
            key: The key to insert or update.
            value: The value to associate with the key.
        """
        if key in self:
            del self[key]
        elif len(self) >= self._max_items:
            self.popitem(last=False)
        super().__setitem__(key, value)


class ThreadSafeFIFODict(FIFODict):
    def __init__(self, max_items=1000, *args, **kwargs):
        self._lock = threading.RLock()
        super().__init__(max_items, *args, **kwargs)

    def __setitem__(self, key, value):
        with self._lock:
            super().__setitem__(key, value)

    def __delitem__(self, key):
        with self._lock:
            super().__delitem__(key)

    def get(self, key, default=None):
        with self._lock:
            return super().get(key, default)

    def keys(self):
        with self._lock:
            return list(super().keys())

    def items(self):
        with self._lock:
            return list(super().items())

    def values(self):
        with self._lock:
            return list(super().values())


class AsyncSafeFIFODict(FIFODict):
    """
    An asyncio-compatible version of FIFODict using asyncio.Lock.

    Suitable for use in asynchronous applications where concurrent coroutine access is expected.

    Parameters:
        max_items (int): The maximum number of items to store.
    """

    def __init__(self, max_items=1000, *args, **kwargs):
        self._lock = asyncio.Lock()
        super().__init__(max_items, *args, **kwargs)

    async def aset(self, key, value):
        """
        Async-safe insert or update with FIFO eviction.

        Parameters:
            key: Key to insert or update.
            value: Value to associate with the key.
        """
        async with self._lock:
            self[key] = value  # Triggers FIFODict.__setitem__

    async def aget(self, key, default=None):
        """
        Async-safe retrieval of a value with a fallback.

        Parameters:
            key: The key to retrieve.
            default: Fallback if key is not found.

        Returns:
            The value or the default.
        """
        async with self._lock:
            return super().get(key, default)

    async def adelete(self, key):
        """
        Async-safe deletion of a key.

        Parameters:
            key: The key to delete.
        """
        async with self._lock:
            del self[key]

    async def acontains(self, key):
        """
        Async-safe existence check for a key.

        Parameters:
            key: The key to check.

        Returns:
            True if the key exists, else False.
        """
        async with self._lock:
            return key in self

    async def akeys(self):
        """Async-safe list of keys."""
        async with self._lock:
            return list(self.keys())

    async def aitems(self):
        """Async-safe list of items."""
        async with self._lock:
            return list(self.items())

    async def avalues(self):
        """Async-safe list of values."""
        async with self._lock:
            return list(self.values())

    async def alen(self):
        """Async-safe length of the dictionary."""
        async with self._lock:
            return len(self)


AsyncFIFODict = AsyncSafeFIFODict
