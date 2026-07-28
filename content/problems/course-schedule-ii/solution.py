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


APPROACHES = [
    {"id": "kahn", "label": "Peel off the ready courses", "fn": kahn,
     "complexity": {"time": "O(V + E)", "space": "O(V)"},
     "viz": {"adj": "graph", "waiting": "labels:adj", "order": "queue", "ready": "queue"}},
]
