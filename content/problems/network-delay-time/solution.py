META = {
    "slug": "network-delay-time",
    "title": "Network Delay Time",
    "pattern": "Advanced Graphs",
    "difficulty": "Medium",
    "leetcode": 743,
    "prompt": (
        "A signal starts at one node of a directed weighted network and travels "
        "along every edge it can. Return how long until all nodes have received "
        "it, or -1 if some node never does."
    ),
    "examples": [
        {"input": "times = [[2,1,1],[2,3,1],[3,4,1]], n = 4, k = 2", "output": "2",
         "why": "Node 4 is the last to hear, two units after the signal leaves node 2."},
        {"input": "times = [[1,2,1]], n = 2, k = 2", "output": "-1",
         "why": "Starting at 2, there is no edge back to 1."},
    ],
    "constraints": ["1 <= n <= 100", "All edge weights are positive"],
}

NET = {1: [], 2: [[1, 1], [3, 1]], 3: [[4, 1]], 4: []}
LOOP = {1: [[2, 4], [3, 1]], 2: [[4, 1]], 3: [[2, 1]], 4: [[1, 7]]}

VARIANTS = [
    {"id": "typical", "label": "Reaches all", "input": {"adj": NET, "start": 2}},
    {"id": "edge", "label": "Unreachable node", "input": {"adj": NET, "start": 3}},
    {"id": "worst-case", "label": "Shorter path wins", "input": {"adj": LOOP, "start": 1}},
]

INF = "∞"


def dijkstra(adj, start):
    #> Nothing is known to be reachable yet except where the signal starts.
    dist = {str(k): INF for k in adj}
    dist[str(start)] = 0
    done = []
    while True:
        #> Settle the nearest unsettled node. Because all weights are positive,
        #> nothing found later can ever improve on it — that's why this is safe.
        best, bestd = None, None
        for k in dist:
            if k not in done and dist[k] != INF and (bestd is None or dist[k] < bestd):
                best, bestd = k, dist[k]
        if best is None:
            #> Everything still reachable has been settled; the rest never will be.
            break
        done.append(best)
        for edge in adj[int(best)]:
            to, w = str(edge[0]), edge[1]
            #> Relaxation: arriving via `best` beats whatever route we had before.
            if dist[to] == INF or bestd + w < dist[to]:
                dist[to] = bestd + w
    #> The signal is done when the slowest node has heard it — so take the max.
    slowest = 0
    for k in dist:
        if dist[k] == INF:
            return -1  #> Someone never heard it at all.
        if dist[k] > slowest:
            slowest = dist[k]
    return slowest


def bellman_ford(adj, start):
    #> No "settle the nearest" step at all: relax every edge, repeatedly, until a
    #> full pass changes nothing. Slower, but it needs no ordering argument —
    #> and unlike Dijkstra it would still work with negative weights.
    dist = {str(k): INF for k in adj}
    dist[str(start)] = 0
    changed = True
    while changed:
        changed = False
        for node in adj:
            here = dist[str(node)]
            if here == INF:
                #> Not reachable yet, so it cannot offer a route to anyone.
                continue
            for edge in adj[node]:
                to, w = str(edge[0]), edge[1]
                #> Arriving via this node beats whatever we had recorded.
                if dist[to] == INF or here + w < dist[to]:
                    dist[to] = here + w
                    changed = True
    #> The answer is the last arrival, and only if every node got one.
    worst = 0
    for k in dist:
        if dist[k] == INF:
            return -1
        if dist[k] > worst:
            worst = dist[k]
    return worst


APPROACHES = [
    {"id": "bellman-ford", "label": "Relax every edge until stable", "fn": bellman_ford,
     "complexity": {"time": "O(V \u00b7 E)", "space": "O(V)"},
     "viz": {"adj": "graph", "dist": "labels:adj"}},
    {
        "id": "dijkstra",
        "label": "Dijkstra",
        "fn": dijkstra,
        "complexity": {"time": "O(V² + E)", "space": "O(V)"},
        "viz": {"adj": "graph", "dist": "labels:adj", "done": "marked:adj"},
    }
]
