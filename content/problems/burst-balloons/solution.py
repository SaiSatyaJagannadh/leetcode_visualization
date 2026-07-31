META = {
    "slug": "burst-balloons",
    "title": "Burst Balloons",
    "pattern": "2-D Dynamic Programming",
    "difficulty": "Hard",
    "leetcode": 312,
    "prompt": "Bursting a balloon earns its value times the values of its current neighbours, and the neighbours then close up. Return the most coins you can collect bursting them all.",
    "examples": [
        {"input": "nums = [3,1,5,8]", "output": "167"},
        {"input": "nums = [1,5]", "output": "10"},
    ],
    "constraints": ["1 <= len(nums) <= 300", "0 <= nums[i] <= 100"],
}

VARIANTS = [
    {"id": "typical", "label": "Four balloons", "input": {"nums": [3, 1, 5, 8]}},
    {"id": "edge", "label": "Two balloons", "input": {"nums": [1, 5]}},
    {"id": "worst-case", "label": "Three balloons", "input": {"nums": [2, 4, 3]}},
]


def last_one_standing(nums):
    #> Pad with 1s so every balloon has neighbours and no bounds check is needed.
    padded = [1] + list(nums) + [1]
    n = len(padded)
    #> dp[lo][hi] is the best from the open range between lo and hi.
    dp = [[0] * n for _ in range(n)]
    #> The trick is choosing which balloon bursts *last* in a range, not first.
    #> Last means its neighbours are the untouched range walls, so the two
    #> sub-ranges become independent — with "first", they wouldn't be.
    for width in range(2, n):
        for lo in range(n - width):
            hi = lo + width
            for k in range(lo + 1, hi):
                gain = padded[lo] * padded[k] * padded[hi]
                total = dp[lo][k] + gain + dp[k][hi]
                if total > dp[lo][hi]:
                    dp[lo][hi] = total
    return dp[0][n - 1]


CACHE = {}


def choose_the_last(nums):
    #> The same insight read top-down: for an open range, try each balloon as the
    #> LAST to burst there. Its neighbours are then the untouched walls, so the
    #> two halves never interfere and can be solved independently.
    CACHE.clear()
    padded = [1] + list(nums) + [1]
    return _best(padded, 0, len(padded) - 1)


def _best(padded, lo, hi):
    if hi - lo < 2:
        #> Nothing strictly between the walls, so nothing to burst.
        return 0
    key = str(lo) + ":" + str(hi)
    if key in CACHE:
        return CACHE[key]
    out = 0
    for k in range(lo + 1, hi):
        #> k bursts last, so it is worth walls times itself, plus whatever the
        #> two independent halves were worth.
        gain = padded[lo] * padded[k] * padded[hi]
        total = _best(padded, lo, k) + gain + _best(padded, k, hi)
        if total > out:
            out = total
    CACHE[key] = out
    return out


APPROACHES = [
    {"id": "top-down", "label": "Pick the last to burst", "fn": choose_the_last,
     "complexity": {"time": "O(n\u00b3)", "space": "O(n\u00b2)"},
     "viz": {"padded": "array", "CACHE": "map", "$calls": "recursion"}},
    {"id": "last", "label": "Pick the last balloon in each range", "fn": last_one_standing,
     "complexity": {"time": "O(n³)", "space": "O(n²)"},
     "viz": {"padded": "array", "dp": "grid", "lo": "row:dp", "hi": "col:dp"}},
]
