META = {
    "slug": "cheapest-flights-within-k-stops",
    "title": "Cheapest Flights Within K Stops",
    "pattern": "Advanced Graphs",
    "difficulty": "Medium",
    "leetcode": 787,
    "prompt": "Find the cheapest route from source to destination using at most k stops in between. Return -1 if no such route exists.",
    "examples": [
        {"input": "n = 4, flights = [[0,1,100],[1,2,100],[2,3,100],[0,3,500]], src = 0, dst = 3, k = 1",
         "output": "500", "why": "The cheap chain needs two stops, one more than allowed."},
        {"input": "same flights, k = 2", "output": "300"},
    ],
    "constraints": ["1 <= n <= 100", "0 <= k < n"],
}

F = [[0, 1, 100], [1, 2, 100], [2, 3, 100], [0, 3, 500]]

VARIANTS = [
    {"id": "typical", "label": "k = 1", "input": {"n": 4, "flights": [f[:] for f in F], "src": 0, "dst": 3, "k": 1}},
    {"id": "edge", "label": "Unreachable", "input": {"n": 3, "flights": [[0, 1, 50]], "src": 0, "dst": 2, "k": 1}},
    {"id": "worst-case", "label": "k = 2", "input": {"n": 4, "flights": [f[:] for f in F], "src": 0, "dst": 3, "k": 2}},
]

BIG = 10 ** 9


def bellman_ford(n, flights, src, dst, k):
    #> cost[i] is the cheapest way to reach i using the flights considered so far.
    cost = [BIG] * n
    cost[src] = 0
    for _ in range(k + 1):
        #> One round per allowed hop. Relaxing against a *snapshot* of the previous
        #> round is essential — using the live array would let a single round
        #> chain several flights together and quietly exceed the stop limit.
        snapshot = list(cost)
        for f in flights:
            a, b, price = f[0], f[1], f[2]
            if snapshot[a] != BIG and snapshot[a] + price < cost[b]:
                cost[b] = snapshot[a] + price
    return -1 if cost[dst] == BIG else cost[dst]


def layer_by_layer(n, flights, src, dst, k):
    #> Same idea told forwards: keep only the cities reachable in exactly h hops
    #> and their best price, then take one more hop from each. Because a layer is
    #> built solely from the previous one, the stop limit cannot be exceeded —
    #> the same guarantee the snapshot gives Bellman-Ford, made structural.
    best = [BIG] * n
    best[src] = 0
    layer = {str(src): 0}
    for _ in range(k + 1):
        nxt = {}
        for key in layer:
            a = int(key)
            for f in flights:
                if f[0] != a:
                    continue
                b = f[1]
                price = layer[key] + f[2]
                #> Only worth carrying forward if it beats what we already have.
                if price < best[b]:
                    best[b] = price
                if str(b) not in nxt or price < nxt[str(b)]:
                    nxt[str(b)] = price
        layer = nxt
    return -1 if best[dst] == BIG else best[dst]


APPROACHES = [
    {"id": "layers", "label": "One layer of hops at a time", "fn": layer_by_layer,
     "complexity": {"time": "O(k \u00b7 E)", "space": "O(n)"},
     "viz": {"best": "array", "layer": "map", "nxt": "map", "flights": "array"}},
    {"id": "bellman-ford", "label": "One relaxation round per hop", "fn": bellman_ford,
     "complexity": {"time": "O(k · E)", "space": "O(n)"},
     "viz": {"cost": "array", "snapshot": "array", "flights": "array"}},
]
