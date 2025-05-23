from flipcache import LRUDict


ld = LRUDict(max_items=4)

ld["a"] = 11
ld["b"] = 22
ld["c"] = 33
ld["d"] = 44
_ = ld["a"]  # access 'a'; now 'a' is most recently used
ld["m"] = 55  # evicts 'b' (least recently used)
print(ld.keys())  # odict_keys(['c', 'd', 'a', 'm'])

ld["n"] = 10  # key 'c' gets evicted
print(ld.keys())  # odict_keys(['d', 'a', 'm', 'n'])
