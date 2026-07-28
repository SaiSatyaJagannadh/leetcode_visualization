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


APPROACHES = [
    {"id": "subset-sum", "label": "Which sums are reachable", "fn": subset_sum,
     "complexity": {"time": "O(n · sum)", "space": "O(sum)"},
     "viz": {"nums": "array", "reachable": "array", "a": "pointer:reachable"}},
]
