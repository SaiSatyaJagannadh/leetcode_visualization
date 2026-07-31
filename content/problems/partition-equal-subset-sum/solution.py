META = {
    "slug": "partition-equal-subset-sum",
    "title": "Partition Equal Subset Sum",
    "pattern": "1-D Dynamic Programming",
    "difficulty": "Medium",
    "leetcode": 416,
    "prompt": "Decide whether an array can be split into two groups with the same sum.",
    "examples": [
        {"input": "nums = [1,5,11,5]", "output": "true", "why": "[1,5,5] and [11] both make 11."},
        {"input": "nums = [1,2,3,5]", "output": "false", "why": "The total is odd, so no split is possible."},
    ],
    "constraints": ["1 <= len(nums) <= 200", "1 <= nums[i] <= 100"],
}

VARIANTS = [
    {"id": "typical", "label": "Splits evenly", "input": {"nums": [1, 5, 11, 5]}},
    {"id": "edge", "label": "Odd total", "input": {"nums": [1, 2, 3, 5]}},
    {"id": "worst-case", "label": "Needs every value", "input": {"nums": [2, 2, 3, 5]}},
]


def subset_sum(nums):
    total = 0
    for n in nums:
        total += n
    if total % 2 == 1:
        #> An odd total can't be halved, so this is settled without any work.
        return False
    target = total // 2
    #> reachable[a] means some subset of the values seen so far sums to a.
    reachable = [False] * (target + 1)
    reachable[0] = True
    for n in nums:
        #> Walking *downward* is essential: going up would let this same value be
        #> spent twice within one pass.
        for a in range(target, n - 1, -1):
            if reachable[a - n]:
                reachable[a] = True
    return reachable[target]


CACHE = {}


def choose_each(nums):
    #> The same question as a decision tree: take this value into the subset or
    #> leave it, and see whether the target can be hit exactly. The memo is what
    #> stops the two branches re-deriving each other.
    CACHE.clear()
    total = 0
    for n in nums:
        total += n
    if total % 2 == 1:
        return False
    return _reach(nums, 0, total // 2)


def _reach(nums, i, left):
    if left == 0:
        #> Landed on the target, so this subset works.
        return True
    if left < 0 or i >= len(nums):
        return False
    key = str(i) + ":" + str(left)
    if key in CACHE:
        return CACHE[key]
    #> Take it, or skip it. Only one branch needs to succeed.
    CACHE[key] = _reach(nums, i + 1, left - nums[i]) or _reach(nums, i + 1, left)
    return CACHE[key]


APPROACHES = [
    {"id": "choose", "label": "Take it or leave it", "fn": choose_each,
     "complexity": {"time": "O(n \u00b7 sum)", "space": "O(n \u00b7 sum)"},
     "viz": {"nums": "array", "CACHE": "map", "$calls": "recursion"}},
    {"id": "subset-sum", "label": "Which sums are reachable", "fn": subset_sum,
     "complexity": {"time": "O(n · sum)", "space": "O(sum)"},
     "viz": {"nums": "array", "reachable": "array", "a": "pointer:reachable"}},
]
