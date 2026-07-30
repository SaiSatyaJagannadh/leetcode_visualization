META = {
    "slug": "koko-eating-bananas",
    "title": "Koko Eating Bananas",
    "pattern": "Binary Search",
    "difficulty": "Medium",
    "leetcode": 875,
    "prompt": "Each pile must be finished before moving on, and only one pile can be eaten from per hour. Find the slowest eating speed that still clears every pile within the hours available.",
    "examples": [
        {"input": "piles = [3,6,7,11], h = 8", "output": "4"},
        {"input": "piles = [30,11,23,4,20], h = 5", "output": "30",
         "why": "With exactly as many hours as piles, each pile must go in one hour."},
    ],
    "constraints": ["1 <= len(piles) <= 10^4", "len(piles) <= h <= 10^9"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"piles": [3, 6, 7, 11], "h": 8}},
    {"id": "edge", "label": "One hour per pile", "input": {"piles": [11, 4], "h": 2}},
    {"id": "worst-case", "label": "Plenty of time", "input": {"piles": [3, 6, 7, 11], "h": 20}},
]


def hours_needed(piles, speed):
    total = 0
    for p in piles:
        total += -(-p // speed)  # ceiling division
    return total


def linear_scan(piles, h):
    #> Try every speed from 1 upward and stop at the first that fits.
    speed = 1
    while hours_needed(piles, speed) > h:
        speed += 1
    return speed


def binary_search(piles, h):
    #> The answer has a staircase shape: too slow, too slow, then fast enough
    #> forever after. Binary search finds the edge of a monotone predicate — the
    #> array itself is never sorted here, the *answers* are.
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        if hours_needed(piles, mid) <= h:
            #> This speed works, so nothing faster can be the minimum. Keep mid.
            hi = mid
        else:
            #> Too slow to finish in time, so the answer is strictly faster.
            lo = mid + 1
    #> lo and hi have converged on the slowest workable speed.
    return lo


APPROACHES = [
    {"id": "linear", "label": "Try every speed", "fn": linear_scan,
     "complexity": {"time": "O(n · max)", "space": "O(1)"},
     "viz": {"piles": "array"}},
    {"id": "binary", "label": "Binary search the answer", "fn": binary_search,
     "complexity": {"time": "O(n log max)", "space": "O(1)"},
     "viz": {"piles": "array"}},
]
