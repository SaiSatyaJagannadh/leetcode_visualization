"""Directed and weighted, an edge relaxation that improves a known distance,
and a cycle the traversal must not fall into."""

META = {"slug": "_graph", "title": "Graph renderer", "pattern": "Fixture"}

# 0 -> 1 -> 3 -> 4, with a long direct 0 -> 3 that gets beaten, and 4 -> 1 closing a cycle.
EDGES = {0: [[1, 2], [2, 5], [3, 9]], 1: [[3, 3]], 2: [[3, 1]], 3: [[4, 2]], 4: [[1, 4]]}

VARIANTS = [
    {"id": "typical", "label": "Five nodes", "input": {"adj": EDGES, "start": 0}},
    {"id": "edge", "label": "From a leaf", "input": {"adj": EDGES, "start": 2}},
]


def dijkstra(adj, start):
    dist = {str(k): "∞" for k in adj}  #> Every node starts unreachable.
    dist[str(start)] = 0
    done = []
    while True:
        #> Take the closest node we haven't settled yet.
        best, bestd = None, None
        for k in dist:
            if k not in done and dist[k] != "∞" and (bestd is None or dist[k] < bestd):
                best, bestd = k, dist[k]
        if best is None:
            break
        done.append(best)
        for edge in adj[int(best)]:
            to, w = str(edge[0]), edge[1]
            #> Relaxation: this edge offers a shorter way in than we had.
            if dist[to] == "∞" or bestd + w < dist[to]:
                dist[to] = bestd + w
    return dist


def dfs_cycle(adj, start):
    seen = []
    stack = [start]
    while stack:
        node = stack.pop()
        if node in seen:
            #> Already visited — this is the cycle closing, and we stop here.
            continue
        seen.append(node)
        for edge in adj[node]:
            #> Push every out-neighbour; the seen check is what makes it terminate.
            stack.append(edge[0])
    return seen


APPROACHES = [
    {
        "id": "dijkstra",
        "label": "Dijkstra",
        "fn": dijkstra,
        "complexity": {"time": "O(V²)", "space": "O(V)"},
        "viz": {"adj": "graph", "dist": "labels:adj", "done": "marked:adj"},
    },
    {
        "id": "dfs",
        "label": "DFS with a cycle",
        "fn": dfs_cycle,
        "complexity": {"time": "O(V+E)", "space": "O(V)"},
        "viz": {"adj": "graph", "seen": "marked:adj", "stack": "stack"},
    },
]
