from collections import OrderedDict
from threading import RLock
import asyncio
from typing import Any, Optional


class LRUDict(OrderedDict):
    """
    Least Recently Used dictionary based on OrderedDict.

    Parameters:
        max_items (int): Maximum number of items to store. When the limit is
                         exceeded, the least recently used item is evicted.
        *args, **kwargs: Additional arguments passed to the parent constructor.
    """

    def __init__(self, max_items=1000, *args, **kwargs):
        self._max_items = max_items
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        """
        Insert or update an item in the dictionary.

        If the key already exists, its value is updated and its position is
        marked as most recently used (moved to the end).

        If the key is new and the dictionary has reached its maximum size,
        the least recently used item (the first item) is evicted.

        Parameters:
            key: The key to insert or update.
            value: The value associated with the key.
        """
        if key in self:
            self.move_to_end(key)
        elif len(self) >= self._max_items:
            self.popitem(last=False)
        super().__setitem__(key, value)

    def __getitem__(self, key):
        """
        Retrieve the value associated with the given key.

        Accessing the key marks it as most recently used by moving it
        to the end of the order.

        Parameters:
            key: The key to retrieve.

        Returns:
            The value associated with the key.

        Raises:
            KeyError: If the key is not found.
        """
        value = super().__getitem__(key)
        try:
            self.move_to_end(key)
        except KeyError:
            pass  # Already evicted
        return value

    def get(self, key: Any, default: Optional[Any] = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def mark_as_used(self, key: Any):
        """Explicitly mark a key as recently used, if it still exists."""
        if key in self:
            try:
                self.move_to_end(key)
            except KeyError:
                pass


class ThreadSafeLRUDict(LRUDict):
    """
    A thread-safe Least Recently Used (LRU) dictionary.

    Inherits from `LRUDict` and adds mutual exclusion using `threading.RLock`
    to ensure safe concurrent access from multiple threads.

    This class is designed for multi-threaded environments where dictionary
    reads and writes may happen in parallel. All core operations are protected
    by a reentrant lock to prevent race conditions.

    Parameters:
        max_items (int): Maximum number of items to store. When the limit is
                         exceeded, the least recently used item is evicted.
        *args, **kwargs: Additional arguments passed to the parent constructor.
    """

    def __init__(self, max_items=1000, *args, **kwargs):
        self._lock = RLock()
        super().__init__(max_items, *args, **kwargs)

    def __setitem__(self, key, value):
        """
        Thread-safe insertion or update of a key-value pair.

        If the key already exists, it is moved to the end to mark it as recently used.
        If the dictionary exceeds its maximum capacity, the least recently used item is removed.

        Parameters:
            key: The key to insert or update.
            value: The value associated with the key.
        """
        with self._lock:
            super().__setitem__(key, value)

    def __getitem__(self, key):
        """
        Thread-safe retrieval of the value associated with a key.

        Accessing the key updates its position as the most recently used.

        Parameters:
            key: The key to retrieve.

        Returns:
            The value associated with the key.

        Raises:
            KeyError: If the key does not exist.
        """
        with self._lock:
            return super().__getitem__(key)

    def __delitem__(self, key):
        """
        Thread-safe removal of a key-value pair.

        Parameters:
            key: The key to delete.

        Raises:
            KeyError: If the key does not exist.
        """
        with self._lock:
            return super().__delitem__(key)

    def get(self, key, default=None):
        """
        Thread-safe version of the `dict.get()` method.

        Retrieves the value associated with the key, or returns the default if the key is not present.
        This does not update the LRU order.

        Parameters:
            key: The key to retrieve.
            default: The value to return if the key is not found. Defaults to None.

        Returns:
            The value associated with the key, or the default.
        """
        with self._lock:
            return super().get(key, default)


class AsyncSafeLRUDict(LRUDict):
    """
    An async-safe version of LRUDict using asyncio.Lock.
    Provides async methods to access and mutate the dictionary safely in async environments.
    """

    def __init__(self, max_items=1000, *args, **kwargs):
        self._async_lock = asyncio.Lock()
        super().__init__(max_items, *args, **kwargs)

    async def aset(self, key, value):
        """
        Asynchronously insert or update a key-value pair in the dictionary.

        If the key already exists, it is marked as most recently used.
        If the key is new and the dictionary exceeds its capacity,
        the least recently used item is removed.

        Parameters:
            key: The key to insert or update.
            value: The value associated with the key.
        """
        async with self._async_lock:
            super().__setitem__(key, value)

    async def aget(self, key, default=None):
        """
        Asynchronously retrieve the value for a given key.

        If the key exists, it is marked as most recently used.
        If not, the default value is returned.

        Parameters:
            key: The key to look up.
            default: The value to return if the key is not found. Defaults to None.

        Returns:
            The value associated with the key, or the default if key is not found.
        """
        async with self._async_lock:
            try:
                return super().__getitem__(key)
            except KeyError:
                return default

    async def adelete(self, key):
        """
        Asynchronously delete a key-value pair from the dictionary.

        Parameters:
            key: The key to remove.

        Raises:
            KeyError: If the key is not found.
        """
        async with self._async_lock:
            del self[key]

    async def aclear(self):
        """
        Asynchronously remove all items from the dictionary.
        """
        async with self._async_lock:
            super().clear()

    async def apop(self, key, default=None):
        """
        Asynchronously remove the specified key and return its value.

        If the key is not found, return the default if provided, otherwise raise KeyError.

        Parameters:
            key: The key to pop.
            default: Value to return if key is not found. If not provided, KeyError is raised.

        Returns:
            The value associated with the key, or default if key not found.
        """
        async with self._async_lock:
            return super().pop(key, default)

    async def apopitem(self, last=True):
        """
        Asynchronously remove and return a (key, value) pair.

        Removes the most recently used item if `last=True`, or the least recently used if `last=False`.

        Parameters:
            last: If True (default), pops the most recent item. Otherwise, pops the least recent.

        Returns:
            A tuple containing the removed key and its value.

        Raises:
            KeyError: If the dictionary is empty.
        """
        async with self._async_lock:
            return super().popitem(last=last)

    async def akeys(self):
        """
        Asynchronously return a list of all keys in the dictionary.

        Returns:
            A list of the dictionary's keys.
        """
        async with self._async_lock:
            return list(self.keys())

    async def aitems(self):
        """
        Asynchronously return a list of (key, value) pairs.

        Returns:
            A list of tuples containing the dictionary’s items.
        """
        async with self._async_lock:
            return list(self.items())

    async def avalues(self):
        """
        Asynchronously return a list of all values in the dictionary.

        Returns:
            A list of the dictionary's values.
        """
        async with self._async_lock:
            return list(self.values())

    async def alen(self):
        """
        Asynchronously return the number of items in the dictionary.

        Returns:
            The number of items currently stored.
        """
        async with self._async_lock:
            return len(self)

    async def acontains(self, key):
        """
        Asynchronously check whether a key exists in the dictionary.

        Parameters:
            key: The key to check.

        Returns:
            True if the key exists, False otherwise.
        """
        async with self._async_lock:
            return key in self


AsyncLRUDict = AsyncSafeLRUDict
