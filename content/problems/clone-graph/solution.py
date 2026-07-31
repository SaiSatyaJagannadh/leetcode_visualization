META = {
    "slug": "clone-graph",
    "title": "Clone Graph",
    "pattern": "Graphs",
    "difficulty": "Medium",
    "leetcode": 133,
    "prompt": "Make a deep copy of a connected undirected graph: every node duplicated, every edge rebuilt between the duplicates rather than the originals.",
    "examples": [
        {"input": "adjList = [[2,4],[1,3],[2,4],[1,3]]", "output": "[[2,4],[1,3],[2,4],[1,3]]"},
        {"input": "adjList = [[]]", "output": "[[]]", "why": "A single node with no neighbours."},
    ],
    "constraints": ["0 <= number of nodes <= 100", "The graph is connected"],
}

SQUARE = {1: [2, 4], 2: [1, 3], 3: [2, 4], 4: [1, 3]}
TRIANGLE = {1: [2, 3], 2: [1, 3], 3: [1, 2]}

VARIANTS = [
    {"id": "typical", "label": "Square", "input": {"adj": SQUARE, "start": 1}},
    {"id": "edge", "label": "Single node", "input": {"adj": {1: []}, "start": 1}},
    {"id": "worst-case", "label": "Fully connected", "input": {"adj": TRIANGLE, "start": 1}},
]


def dfs_clone(adj, start):
    #> The map does double duty: it holds the copies, and its keys are the
    #> visited-set. Without that, a cycle would make this recurse forever.
    made = {}
    _copy(adj, start, made)
    #> Rebuild the adjacency of the copy so the result is comparable.
    out = {}
    for key in made:
        out[key] = made[key]
    return out


def _copy(adj, node, made):
    key = str(node)
    if key in made:
        #> Already cloned on an earlier branch, so hand back the same copy —
        #> creating a second one would break the shared structure.
        return made[key]
    #> Register the clone *before* recursing, or a cycle re-enters this node.
    made[key] = []
    for other in adj[node]:
        made[key].append(other)
        _copy(adj, other, made)
    return made[key]


def bfs_clone(adj, start):
    #> Same job without recursion. The map is still the visited-set, so a node
    #> is only ever queued once no matter how many edges point at it.
    made = {}
    made[str(start)] = []
    queue = [start]
    while queue:
        node = queue.pop(0)
        key = str(node)
        for other in adj[node]:
            #> Record the edge on the copy first — that part does not depend on
            #> whether the neighbour has been cloned yet.
            made[key].append(other)
            if str(other) not in made:
                #> First sighting: register the clone, then queue it. Registering
                #> before queueing is what keeps a cycle from queueing it twice.
                made[str(other)] = []
                queue.append(other)
    out = {}
    for key in made:
        out[key] = made[key]
    return out


APPROACHES = [
    {"id": "bfs", "label": "BFS with a clone map", "fn": bfs_clone,
     "complexity": {"time": "O(V + E)", "space": "O(V)"},
     "viz": {"adj": "graph", "made": "map", "queue": "queue"}},
    {"id": "dfs", "label": "DFS with a clone map", "fn": dfs_clone,
     "complexity": {"time": "O(V + E)", "space": "O(V)"},
     "viz": {"adj": "graph", "made": "map", "$calls": "recursion"}},
]
