from collections import OrderedDict

class LRUDict:
    def __init__(self, max_items: int = 1000):
        self._store = OrderedDict()
        self._max_items = max_items

    def __setitem__(self, key, value):
        if key in self._store:
            self._store.move_to_end(key)  # mark as recently used
        elif len(self._store) >= self._max_items:
            self._store.popitem(last=False)  # remove least recently used
        self._store[key] = value

    def __getitem__(self, key):
        value = self._store[key]
        self._store.move_to_end(key)  # mark as recently used
        return value

    def __delitem__(self, key):
        del self._store[key]

    def __contains__(self, key):
        return key in self._store

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __len__(self):
        return len(self._store)

    def keys(self):
        return self._store.keys()

    def items(self):
        return self._store.items()

    def values(self):
        return self._store.values()
