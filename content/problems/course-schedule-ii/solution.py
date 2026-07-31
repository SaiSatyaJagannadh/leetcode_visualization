META = {
    "slug": "course-schedule-ii",
    "title": "Course Schedule II",
    "pattern": "Graphs",
    "difficulty": "Medium",
    "leetcode": 210,
    "prompt": "Return an order in which every course can be taken, respecting all prerequisites. Return an empty list if no such order exists.",
    "examples": [
        {"input": "numCourses = 2, prerequisites = [[1,0]]", "output": "[0,1]"},
        {"input": "numCourses = 2, prerequisites = [[1,0],[0,1]]", "output": "[]"},
    ],
    "constraints": ["1 <= numCourses <= 2000"],
}

OK = {0: [], 1: [0], 2: [0], 3: [1, 2]}
LOOP = {0: [1], 1: [0]}

VARIANTS = [
    {"id": "typical", "label": "Diamond", "input": {"adj": OK}},
    {"id": "edge", "label": "Cycle", "input": {"adj": LOOP}},
    {"id": "worst-case", "label": "Chain", "input": {"adj": {0: [], 1: [0], 2: [1]}}},
]


def kahn(adj):
    #> How many prerequisites each course is still waiting on.
    waiting = {str(k): len(adj[k]) for k in adj}
    #> Anything waiting on nothing can be taken right now.
    ready = [k for k in adj if waiting[str(k)] == 0]
    order = []
    while ready:
        course = ready.pop(0)
        order.append(course)
        for other in adj:
            #> Taking this course releases everything that required it.
            if course in adj[other]:
                waiting[str(other)] -= 1
                if waiting[str(other)] == 0:
                    ready.append(other)
    #> If some course never reached zero, it sat in a cycle waiting forever.
    return order if len(order) == len(adj) else []


ORDER = []


def dfs_postorder(adj):
    #> The other classic topological sort: finish a course's prerequisites, then
    #> record the course. Postorder is what makes the list come out in order.
    ORDER.clear()
    state = {str(k): "new" for k in adj}
    for course in adj:
        if not _visit(adj, course, state):
            #> A cycle makes any ordering impossible, so nothing is returned.
            return []
    return [c for c in ORDER]


def _visit(adj, course, state):
    key = str(course)
    if state[key] == "doing":
        #> Reached a course still on the current path: that is the cycle.
        return False
    if state[key] == "done":
        return True
    state[key] = "doing"
    for need in adj[course]:
        if not _visit(adj, need, state):
            return False
    state[key] = "done"
    #> Recorded only after every prerequisite is already in the list, so the
    #> ordering is correct by construction rather than by counting.
    ORDER.append(course)
    return True


APPROACHES = [
    {"id": "dfs-postorder", "label": "DFS, record on the way out", "fn": dfs_postorder,
     "complexity": {"time": "O(V + E)", "space": "O(V)"},
     "viz": {"adj": "graph", "state": "labels:adj", "ORDER": "queue", "$calls": "recursion"}},
    {"id": "kahn", "label": "Peel off the ready courses", "fn": kahn,
     "complexity": {"time": "O(V + E)", "space": "O(V)"},
     "viz": {"adj": "graph", "waiting": "labels:adj", "order": "queue", "ready": "queue"}},
]
