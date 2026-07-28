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


APPROACHES = [
    {"id": "union-find", "label": "Union-find", "fn": union_find,
     "complexity": {"time": "O(E · α(V))", "space": "O(V)"},
     "viz": {"edges": "array", "parent": "map"}},
]
