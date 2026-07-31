META = {
    "slug": "min-cost-to-connect-all-points",
    "title": "Min Cost to Connect All Points",
    "pattern": "Advanced Graphs",
    "difficulty": "Medium",
    "leetcode": 1584,
    "prompt": "Connect every point so all are reachable, paying the Manhattan distance for each connection. Return the cheapest total.",
    "examples": [
        {"input": "points = [[0,0],[2,2],[3,10],[5,2],[7,0]]", "output": "20"},
        {"input": "points = [[3,12],[-2,5],[-4,1]]", "output": "18"},
    ],
    "constraints": ["1 <= len(points) <= 1000"],
}

VARIANTS = [
    {"id": "typical", "label": "Five points", "input": {"points": [[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]]}},
    {"id": "edge", "label": "Single point", "input": {"points": [[1, 1]]}},
    {"id": "worst-case", "label": "Collinear", "input": {"points": [[0, 0], [1, 0], [2, 0], [3, 0]]}},
]

BIG = 10 ** 9


def prim(points):
    n = len(points)
    #> Grow one tree outward. `best[i]` is the cheapest known edge from the tree
    #> to point i, which is the only thing worth remembering about the outside.
    inside = [False] * n
    best = [BIG] * n
    best[0] = 0
    total = 0
    for _ in range(n):
        #> Take the cheapest edge crossing out of the tree. That edge is always
        #> safe to add — no cheaper way to reach that point can exist later.
        pick = -1
        for i in range(n):
            if not inside[i] and (pick == -1 or best[i] < best[pick]):
                pick = i
        inside[pick] = True
        total += best[pick]
        for i in range(n):
            if not inside[i]:
                d = abs(points[pick][0] - points[i][0]) + abs(points[pick][1] - points[i][1])
                if d < best[i]:
                    #> Joining `pick` may have brought the tree closer to point i.
                    best[i] = d
    return total


def kruskal(points):
    #> The other classic spanning tree: forget growing one blob outward, just
    #> sort every possible edge and take the cheap ones that join two groups
    #> that were not already connected.
    n = len(points)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            d = abs(points[i][0] - points[j][0]) + abs(points[i][1] - points[j][1])
            edges.append([d, i, j])
    edges = sorted(edges, key=lambda e: e[0])
    parent = [i for i in range(n)]
    total = 0
    for e in edges:
        a = _root(parent, e[1])
        b = _root(parent, e[2])
        if a == b:
            #> Already connected, so this edge would only close a cycle.
            continue
        #> Cheapest edge joining two separate groups is always safe to take.
        parent[a] = b
        total += e[0]
    return total


def _root(parent, x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


APPROACHES = [
    {"id": "kruskal", "label": "Sort every edge, join groups", "fn": kruskal,
     "complexity": {"time": "O(n\u00b2 log n)", "space": "O(n\u00b2)"},
     "viz": {"points": "array", "edges": "array", "parent": "array"}},
    {"id": "prim", "label": "Prim's algorithm", "fn": prim,
     "complexity": {"time": "O(n²)", "space": "O(n)"},
     "viz": {"points": "array", "best": "array", "inside": "array", "pick": "pointer:best"}},
]
