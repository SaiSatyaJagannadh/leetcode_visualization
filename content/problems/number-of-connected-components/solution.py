META = {
    "slug": "number-of-connected-components",
    "title": "Number of Connected Components",
    "pattern": "Graphs",
    "difficulty": "Medium",
    "leetcode": 323,
    "prompt": "Given an undirected graph, count the groups of nodes that are reachable from one another.",
    "examples": [
        {"input": "n = 5, edges = [[0,1],[1,2],[3,4]]", "output": "2"},
        {"input": "n = 5, edges = [[0,1],[1,2],[2,3],[3,4]]", "output": "1"},
    ],
    "constraints": ["1 <= n <= 2000", "No duplicate edges"],
}

TWO = {0: [1], 1: [0, 2], 2: [1], 3: [4], 4: [3]}
ONE = {0: [1], 1: [0, 2], 2: [1, 3], 3: [2]}
ISOLATED = {0: [], 1: [], 2: []}

VARIANTS = [
    {"id": "typical", "label": "Two groups", "input": {"adj": TWO}},
    {"id": "edge", "label": "All isolated", "input": {"adj": ISOLATED}},
    {"id": "worst-case", "label": "One chain", "input": {"adj": ONE}},
]


def union_find(adj):
    #> Each node starts as its own group; parent[x] points one step toward the
    #> group's representative.
    parent = {str(k): str(k) for k in adj}
    groups = len(adj)
    for node in adj:
        for other in adj[node]:
            ra = _find(parent, str(node))
            rb = _find(parent, str(other))
            if ra != rb:
                #> Two separate groups just became one, so the count drops.
                parent[ra] = rb
                groups -= 1
    return groups


def _find(parent, x):
    #> Walk to the representative, flattening the path so later lookups are quick.
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def walk_each_group(adj):
    #> No union-find: start a fresh walk from every unvisited node and sweep up
    #> everything it can reach. Each walk that starts is exactly one component.
    seen = {}
    groups = 0
    for node in adj:
        if str(node) in seen:
            #> Already swallowed by an earlier walk, so it starts nothing new.
            continue
        groups += 1
        stack = [node]
        while stack:
            cur = stack.pop()
            if str(cur) in seen:
                continue
            seen[str(cur)] = True
            for other in adj[cur]:
                stack.append(other)
    return groups


APPROACHES = [
    {"id": "walk", "label": "One walk per group", "fn": walk_each_group,
     "complexity": {"time": "O(V + E)", "space": "O(V)"},
     "viz": {"adj": "graph", "seen": "marked:adj", "stack": "stack"}},
    {"id": "union-find", "label": "Union-find", "fn": union_find,
     "complexity": {"time": "O(E · α(V))", "space": "O(V)"},
     "viz": {"adj": "graph", "parent": "labels:adj"}},
]
