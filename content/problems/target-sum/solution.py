META = {
    "slug": "target-sum",
    "title": "Target Sum",
    "pattern": "2-D Dynamic Programming",
    "difficulty": "Medium",
    "leetcode": 494,
    "prompt": "Put a plus or minus in front of every number so the expression evaluates to the target. Count the ways.",
    "examples": [
        {"input": "nums = [1,1,1,1,1], target = 3", "output": "5"},
        {"input": "nums = [1], target = 1", "output": "1"},
    ],
    "constraints": ["1 <= len(nums) <= 20", "0 <= sum(nums) <= 1000"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"nums": [1, 1, 1, 1, 1], "target": 3}},
    {"id": "edge", "label": "Single value", "input": {"nums": [1], "target": 1}},
    {"id": "worst-case", "label": "Unreachable", "input": {"nums": [1, 2], "target": 7}},
]


def running_totals(nums, target):
    #> Track how many sign choices land on each running total. One pass per
    #> number, branching every total into a plus and a minus version.
    counts = {0: 1}
    for n in nums:
        nxt = {}
        for total in counts:
            for signed in (total + n, total - n):
                #> Different sign choices reaching the same total merge here,
                #> which is what keeps this from being 2ⁿ separate branches.
                nxt[signed] = nxt.get(signed, 0) + counts[total]
        counts = nxt
    return counts.get(target, 0)


CACHE = {}


def choose_each_sign(nums, target):
    #> The literal question: pick a sign for each number and count the ways to
    #> land on the target. Keyed on (position, running total), the memo merges
    #> branches that arrived at the same place — the same merging the forward
    #> pass gets for free by storing totals in a map.
    CACHE.clear()
    return _ways(nums, target, 0, 0)


def _ways(nums, target, i, total):
    if i == len(nums):
        #> Every number has a sign now, so this is one complete assignment.
        return 1 if total == target else 0
    key = str(i) + ":" + str(total)
    if key in CACHE:
        return CACHE[key]
    #> Both signs are always available; the counts add.
    CACHE[key] = _ways(nums, target, i + 1, total + nums[i]) + _ways(nums, target, i + 1, total - nums[i])
    return CACHE[key]


APPROACHES = [
    {"id": "choose", "label": "Pick a sign, memoised", "fn": choose_each_sign,
     "complexity": {"time": "O(n \u00b7 sum)", "space": "O(n \u00b7 sum)"},
     "viz": {"nums": "array", "CACHE": "map", "$calls": "recursion"}},
    {"id": "totals", "label": "Count reachable totals", "fn": running_totals,
     "complexity": {"time": "O(n · sum)", "space": "O(sum)"},
     "viz": {"nums": "array", "counts": "map", "nxt": "map"}},
]
