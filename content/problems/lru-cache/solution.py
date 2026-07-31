META = {
    "slug": "lru-cache",
    "title": "LRU Cache",
    "pattern": "Linked List",
    "difficulty": "Medium",
    "leetcode": 146,
    "prompt": "A cache of fixed capacity. Reading or writing a key makes it the most recently used; when the cache is full, the least recently used key is evicted. Both operations must be constant time.",
    "examples": [
        {"input": "capacity 2: put(1,1), put(2,2), get(1)", "output": "1"},
        {"input": "put(3,3) then get(2)", "output": "-1", "why": "Key 2 was the least recently used, so it was evicted."},
    ],
    "constraints": ["1 <= capacity <= 3000", "get and put must be O(1)"],
}

VARIANTS = [
    {"id": "typical", "label": "Eviction",
     "input": {"cap": 2, "ops": [["put", 1, 1], ["put", 2, 2], ["get", 1, 0], ["put", 3, 3], ["get", 2, 0]]}},
    {"id": "edge", "label": "Capacity one",
     "input": {"cap": 1, "ops": [["put", 1, 1], ["put", 2, 2], ["get", 1, 0]]}},
    {"id": "worst-case", "label": "Repeated reads keep it alive",
     "input": {"cap": 2, "ops": [["put", 1, 1], ["put", 2, 2], ["get", 1, 0], ["get", 1, 0], ["put", 3, 3], ["get", 1, 0]]}},
]


def ordered_map(cap, ops):
    #> `order` lists keys oldest-first; `store` holds the values. Together they
    #> give O(1) lookup plus a known eviction victim. A real implementation uses
    #> a doubly linked list so the reorder below is O(1) rather than O(n).
    store = {}
    order = []
    out = []
    for op in ops:
        kind, key, value = op[0], op[1], op[2]
        if kind == "get":
            if key not in store:
                out.append(-1)
                continue
            #> A hit counts as use, so the key moves to the recent end.
            order.remove(key)
            order.append(key)
            out.append(store[key])
        else:
            if key in store:
                order.remove(key)
            elif len(store) >= cap:
                #> Full and this is a new key, so the oldest one has to go.
                victim = order.pop(0)
                del store[victim]
            store[key] = value
            order.append(key)
    return out


def stamped(cap, ops):
    #> No ordering list at all: give every entry the clock value at its last use
    #> and, when eviction is needed, scan for the smallest stamp. The order list
    #> exists precisely to turn that scan into a pop.
    clock = [0]
    store = {}
    used = {}
    out = []
    for op in ops:
        kind, key, value = op[0], op[1], op[2]
        clock[0] += 1
        if kind == "get":
            if key not in store:
                out.append(-1)
                continue
            #> A hit refreshes the stamp, which is what "recently used" means here.
            used[key] = clock[0]
            out.append(store[key])
        else:
            if key not in store and len(store) >= cap:
                #> Full and this key is new, so find the least recently used.
                victim = None
                for k in used:
                    if victim is None or used[k] < used[victim]:
                        victim = k
                del store[victim]
                del used[victim]
            store[key] = value
            used[key] = clock[0]
    return out


APPROACHES = [
    {"id": "stamped", "label": "Timestamp every entry", "fn": stamped,
     "complexity": {"time": "O(n) per eviction", "space": "O(n)"},
     "viz": {"store": "map", "used": "map", "out": "queue"}},
    {"id": "ordered", "label": "Map plus recency order", "fn": ordered_map,
     "complexity": {"time": "O(1) amortised", "space": "O(capacity)"},
     "viz": {"store": "map", "order": "queue", "out": "queue"}},
]
