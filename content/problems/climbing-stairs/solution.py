META = {
    "slug": "climbing-stairs",
    "title": "Climbing Stairs",
    "pattern": "1-D Dynamic Programming",
    "difficulty": "Easy",
    "leetcode": 70,
    "prompt": (
        "You climb a staircase of n steps, taking either one or two steps at a "
        "time. Count the distinct ways to reach the top."
    ),
    "examples": [
        {"input": "n = 2", "output": "2", "why": "1+1, or 2."},
        {"input": "n = 3", "output": "3", "why": "1+1+1, 1+2, or 2+1."},
    ],
    "constraints": ["1 <= n <= 45"],
}

VARIANTS = [
    {"id": "typical", "label": "n = 6", "input": {"n": 6}},
    {"id": "edge", "label": "n = 1", "input": {"n": 1}},
    {"id": "worst-case", "label": "n = 10", "input": {"n": 10}},
]


def naive(n):
    #> The last move onto step n came from either step n-1 or step n-2,
    #> so the ways to reach n are the ways to reach those two, added.
    if n <= 2:
        return n  #> One step has one route, two steps have two.
    return naive(n - 1) + naive(n - 2)


def bottom_up(n):
    if n <= 2:
        return n
    #> Same recurrence, but built upward so no subproblem is ever solved twice.
    ways = [0] * (n + 1)
    ways[1] = 1
    ways[2] = 2
    for i in range(3, n + 1):
        #> Everything this line needs was already filled in on earlier passes.
        ways[i] = ways[i - 1] + ways[i - 2]
    return ways[n]


APPROACHES = [
    {
        "id": "naive",
        "label": "Naive recursion",
        "fn": naive,
        "complexity": {"time": "O(2ⁿ)", "space": "O(n)"},
        "viz": {"$calls": "recursion"},
    },
    {
        "id": "bottom-up",
        "label": "Bottom-up table",
        "fn": bottom_up,
        "complexity": {"time": "O(n)", "space": "O(n)"},
        "viz": {"ways": "array", "i": "pointer:ways"},
    },
]
