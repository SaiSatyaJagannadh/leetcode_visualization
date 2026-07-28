META = {
    "slug": "course-schedule",
    "title": "Course Schedule",
    "pattern": "Graphs",
    "difficulty": "Medium",
    "leetcode": 207,
    "prompt": "Some courses require others first. Decide whether every course can be completed, which fails exactly when the prerequisites form a cycle.",
    "examples": [
        {"input": "numCourses = 2, prerequisites = [[1,0]]", "output": "true"},
        {"input": "numCourses = 2, prerequisites = [[1,0],[0,1]]", "output": "false",
         "why": "Each needs the other first, so neither can start."},
    ],
    "constraints": ["1 <= numCourses <= 2000"],
}

OK = {0: [], 1: [0], 2: [1], 3: [1]}
LOOP = {0: [1], 1: [0]}
LONG = {0: [], 1: [0], 2: [1], 3: [2], 4: [3]}

VARIANTS = [
    {"id": "typical", "label": "Completable", "input": {"adj": OK}},
    {"id": "edge", "label": "Two-course cycle", "input": {"adj": LOOP}},
    {"id": "worst-case", "label": "Long chain", "input": {"adj": LONG}},
]


def detect_cycle(adj):
    #> Three states per course: untouched, on the current path, and fully cleared.
    #> Meeting a course that's on the current path is the definition of a cycle.
    state = {str(k): "new" for k in adj}
    for course in adj:
        if not _visit(adj, course, state):
            return False
    return True


def _visit(adj, course, state):
    key = str(course)
    if state[key] == "doing":
        #> We reached a course we're still in the middle of — a cycle.
        return False
    if state[key] == "done":
        #> Already cleared on an earlier walk, so it can't cause trouble now.
        return True
    state[key] = "doing"
    for need in adj[course]:
        if not _visit(adj, need, state):
            return False
    #> Everything this course depends on is clear, so it is too, permanently.
    state[key] = "done"
    return True


APPROACHES = [
    {"id": "dfs", "label": "DFS with three colours", "fn": detect_cycle,
     "complexity": {"time": "O(V + E)", "space": "O(V)"},
     "viz": {"adj": "graph", "state": "labels:adj", "$calls": "recursion"}},
]
