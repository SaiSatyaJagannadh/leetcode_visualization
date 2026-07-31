META = {
    "slug": "graph-valid-tree",
    "title": "Graph Valid Tree",
    "pattern": "Graphs",
    "difficulty": "Medium",
    "leetcode": 261,
    "prompt": "Decide whether an undirected graph is a tree: fully connected, with no cycles.",
    "examples": [
        {"input": "n = 5, edges = [[0,1],[0,2],[0,3],[1,4]]", "output": "true"},
        {"input": "n = 5, edges = [[0,1],[1,2],[2,3],[1,3],[1,4]]", "output": "false",
         "why": "The edges 1-2, 2-3, 1-3 close a cycle."},
    ],
    "constraints": ["1 <= n <= 2000", "No self-loops or duplicate edges"],
}

TREE = {0: [1, 2, 3], 1: [0, 4], 2: [0], 3: [0], 4: [1]}
CYCLE = {0: [1], 1: [0, 2, 3], 2: [1, 3], 3: [1, 2]}
SPLIT = {0: [1], 1: [0], 2: [3], 3: [2]}

VARIANTS = [
    {"id": "typical", "label": "Is a tree", "input": {"adj": TREE}},
    {"id": "edge", "label": "Has a cycle", "input": {"adj": CYCLE}},
    {"id": "worst-case", "label": "Disconnected", "input": {"adj": SPLIT}},
]


def count_edges_and_walk(adj):
    #> A tree on n nodes has exactly n - 1 edges. Fewer means it's disconnected,
    #> more means it must contain a cycle — so this check does half the work.
    edge_count = 0
    for node in adj:
        edge_count += len(adj[node])
    edge_count = edge_count // 2
    if edge_count != len(adj) - 1:
        return False
    #> With the edge count right, connectivity is the only remaining question:
    #> reach everything from one node and a cycle becomes impossible.
    seen = {}
    stack = [next(iter(adj))]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen[node] = True
        for other in adj[node]:
            stack.append(other)
    return len(seen) == len(adj)


def union_find(adj):
    #> Merge nodes into groups one edge at a time. If an edge joins two nodes
    #> already in the same group, that edge closes a cycle — detected the moment
    #> it happens, with no traversal and no edge-count shortcut.
    parent = {str(k): str(k) for k in adj}
    joins = 0
    for node in adj:
        for other in adj[node]:
            if node > other:
                #> Each undirected edge appears twice; take it once.
                continue
            a = _root(parent, str(node))
            b = _root(parent, str(other))
            if a == b:
                #> Already connected, so this edge is the cycle.
                return False
            parent[a] = b
            joins += 1
    #> n - 1 successful merges means everything ended up in one group.
    return joins == len(adj) - 1


def _root(parent, x):
    while parent[x] != x:
        #> Point straight at the grandparent while walking up, which keeps the
        #> chains short for every later lookup.
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


APPROACHES = [
    {"id": "union-find", "label": "Union-find", "fn": union_find,
     "complexity": {"time": "O(E \u00b7 \u03b1)", "space": "O(V)"},
     "viz": {"adj": "graph", "parent": "labels:adj"}},
    {"id": "count-walk", "label": "Count edges, then walk", "fn": count_edges_and_walk,
     "complexity": {"time": "O(V + E)", "space": "O(V)"},
     "viz": {"adj": "graph", "seen": "marked:adj", "stack": "stack"}},
]
