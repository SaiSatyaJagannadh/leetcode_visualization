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


APPROACHES = [
    {"id": "totals", "label": "Count reachable totals", "fn": running_totals,
     "complexity": {"time": "O(n · sum)", "space": "O(sum)"},
     "viz": {"nums": "array", "counts": "map", "nxt": "map"}},
]
