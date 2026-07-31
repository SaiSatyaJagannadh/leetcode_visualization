META = {
    "slug": "min-cost-climbing-stairs",
    "title": "Min Cost Climbing Stairs",
    "pattern": "1-D Dynamic Programming",
    "difficulty": "Easy",
    "leetcode": 746,
    "prompt": "Each step charges a fee to stand on. You may start on step 0 or step 1 and climb one or two steps at a time. Return the cheapest way to get past the top.",
    "examples": [
        {"input": "cost = [10,15,20]", "output": "15", "why": "Start on 15 and take two steps."},
        {"input": "cost = [1,100,1,1,1,100,1,1,100,1]", "output": "6"},
    ],
    "constraints": ["2 <= len(cost) <= 1000"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"cost": [10, 15, 20]}},
    {"id": "edge", "label": "Two steps", "input": {"cost": [5, 3]}},
    {"id": "worst-case", "label": "Expensive traps", "input": {"cost": [1, 100, 1, 1, 1, 100, 1]}},
]


def bottom_up(cost):
    n = len(cost)
    #> best[i] is the cheapest way to *arrive* at step i. Arriving is free at the
    #> two starting steps; the fee is only charged on the way out.
    best = [0] * (n + 1)
    for i in range(2, n + 1):
        #> Arrive from one step back or two, whichever total is cheaper.
        best[i] = min(best[i - 1] + cost[i - 1], best[i - 2] + cost[i - 2])
    #> Position n is past the top, which is where we wanted to end up.
    return best[n]


MEMO = {}


def top_down(cost):
    #> Asked from the top instead of built from the bottom: what does it cost to
    #> finish from step i? The two starting steps are both legal entry points.
    MEMO.clear()
    return min(_from(cost, 0), _from(cost, 1))


def _from(cost, i):
    if i >= len(cost):
        #> Past the top, so nothing left to pay.
        return 0
    if i in MEMO:
        return MEMO[i]
    #> Pay this step's fee, then take one or two steps, whichever finishes cheaper.
    MEMO[i] = cost[i] + min(_from(cost, i + 1), _from(cost, i + 2))
    return MEMO[i]


APPROACHES = [
    {"id": "top-down", "label": "Cost to finish from here", "fn": top_down,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"cost": "array", "MEMO": "map", "$calls": "recursion"}},
    {"id": "bottom-up", "label": "Bottom-up", "fn": bottom_up,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"cost": "array", "best": "array", "i": "pointer:best"}},
]
