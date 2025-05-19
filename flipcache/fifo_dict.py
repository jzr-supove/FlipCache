from collections import OrderedDict

class FIFODict:
    def __init__(self, max_items: int = 1000):
        self._store = OrderedDict()
        self._max_items = max_items

    def __setitem__(self, key, value):
        if key in self._store:
            del self._store[key]  # move to end (new insert)
        elif len(self._store) >= self._max_items:
            self._store.popitem(last=False)  # evict oldest
        self._store[key] = value

    def __getitem__(self, key):
        return self._store[key]

    def __delitem__(self, key):
        del self._store[key]

    def __contains__(self, key):
        return key in self._store

    def get(self, key, default=None):
        return self._store.get(key, default)

    def __len__(self):
        return len(self._store)

    def keys(self):
        return self._store.keys()

    def items(self):
        return self._store.items()

    def values(self):
        return self._store.values()
