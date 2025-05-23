from flipcache import FIFODict


fd = FIFODict(max_items=4)

fd["a"] = 1
fd["b"] = 2
fd["c"] = 3
fd["d"] = 4
_ = fd["a"]  # accessing key 'a' - doesn't change its position
fd["e"] = 5  # key 'a' gets dropped
print(fd.keys())  # odict_keys(['b', 'c', 'd', 'e'])

fd["b"] = 10
# key 'b' moves to the front, so the key 'c' will be out in the next insertion
print(fd.keys())  # odict_keys(['c', 'd', 'e', 'b'])

fd["il"] = 20  # key 'c' gets dropped
print(fd.keys())  # odict_keys(['d', 'e', 'b', 'il'])
