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


APPROACHES = [
    {"id": "prim", "label": "Prim's algorithm", "fn": prim,
     "complexity": {"time": "O(n²)", "space": "O(n)"},
     "viz": {"points": "array", "best": "array", "inside": "array", "pick": "pointer:best"}},
]
