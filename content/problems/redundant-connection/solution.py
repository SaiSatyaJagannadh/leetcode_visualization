META = {
    "slug": "redundant-connection",
    "title": "Redundant Connection",
    "pattern": "Graphs",
    "difficulty": "Medium",
    "leetcode": 684,
    "prompt": "A tree had one extra edge added, creating exactly one cycle. Return the added edge — the last one in the input that closes a loop.",
    "examples": [
        {"input": "edges = [[1,2],[1,3],[2,3]]", "output": "[2,3]"},
        {"input": "edges = [[1,2],[2,3],[3,4],[1,4],[1,5]]", "output": "[1,4]"},
    ],
    "constraints": ["3 <= number of edges <= 1000", "Exactly one cycle exists"],
}

VARIANTS = [
    {"id": "typical", "label": "Small cycle", "input": {"edges": [[1, 2], [1, 3], [2, 3]]}},
    {"id": "edge", "label": "Cycle closes late", "input": {"edges": [[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]}},
    {"id": "worst-case", "label": "Long chain first", "input": {"edges": [[1, 2], [2, 3], [3, 4], [4, 5], [1, 5]]}},
]


def union_find(edges):
    parent = {}
    for edge in edges:
        for node in edge:
            if str(node) not in parent:
                parent[str(node)] = str(node)
    for edge in edges:
        a, b = _find(parent, str(edge[0])), _find(parent, str(edge[1]))
        if a == b:
            #> Both endpoints already share a group, so this edge closes a loop.
            #> Processing edges in order means the first such edge we hit is the
            #> last one that could have been added — exactly what's wanted.
            return edge
        parent[a] = b  #> Otherwise merge the two groups and carry on.
    return []


def _find(parent, x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def rebuild_and_walk(edges):
    #> No union-find: add edges one at a time and, before each, ask whether the
    #> two endpoints can already reach each other. The first time they can, that
    #> edge closes the cycle. Same answer, a whole traversal per edge.
    adj = {}
    for edge in edges:
        for node in edge:
            if str(node) not in adj:
                adj[str(node)] = []
    for edge in edges:
        a, b = str(edge[0]), str(edge[1])
        if _reaches(adj, a, b):
            #> Already connected, so this edge is the redundant one.
            return edge
        adj[a].append(b)
        adj[b].append(a)
    return []


def _reaches(adj, start, goal):
    seen = {}
    stack = [start]
    while stack:
        cur = stack.pop()
        if cur == goal:
            return True
        if cur in seen:
            continue
        seen[cur] = True
        for other in adj[cur]:
            stack.append(other)
    #> Ran out of places to go without arriving.
    return False


APPROACHES = [
    {"id": "walk", "label": "Walk before adding each edge", "fn": rebuild_and_walk,
     "complexity": {"time": "O(E\u00b2)", "space": "O(V + E)"},
     "viz": {"adj": "graph", "seen": "marked:adj", "stack": "stack"}},
    {"id": "union-find", "label": "Union-find", "fn": union_find,
     "complexity": {"time": "O(E · α(V))", "space": "O(V)"},
     "viz": {"edges": "array", "parent": "map"}},
]
