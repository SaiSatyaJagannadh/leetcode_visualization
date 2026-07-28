META = {
    "slug": "longest-increasing-subsequence",
    "title": "Longest Increasing Subsequence",
    "pattern": "1-D Dynamic Programming",
    "difficulty": "Medium",
    "leetcode": 300,
    "prompt": "Return the length of the longest strictly increasing subsequence. The chosen numbers keep their order but need not be adjacent.",
    "examples": [
        {"input": "nums = [10,9,2,5,3,7,101,18]", "output": "4", "why": "2, 3, 7, 101."},
        {"input": "nums = [7,7,7,7]", "output": "1", "why": "Strictly increasing, so equal values don't chain."},
    ],
    "constraints": ["1 <= len(nums) <= 2500"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"nums": [10, 9, 2, 5, 3, 7, 101, 18]}},
    {"id": "edge", "label": "All equal", "input": {"nums": [7, 7, 7]}},
    {"id": "worst-case", "label": "Descending", "input": {"nums": [5, 4, 3, 2]}},
]


def quadratic(nums):
    #> best[i] is the longest increasing run that *ends* at i. Anchoring on the
    #> end is what makes the subproblems combine.
    best = [1] * len(nums)
    for i in range(len(nums)):
        for j in range(i):
            #> Any earlier smaller value can be extended by nums[i].
            if nums[j] < nums[i] and best[j] + 1 > best[i]:
                best[i] = best[j] + 1
    top = 0
    for b in best:
        top = max(top, b)
    return top


def patience(nums):
    #> tails[k] is the smallest value that any length-(k+1) run can end on.
    #> Keeping each length's ending as small as possible leaves the most room
    #> for future numbers. tails is sorted, so the search can be binary.
    tails = []
    for n in nums:
        lo, hi = 0, len(tails)
        while lo < hi:
            mid = (lo + hi) // 2
            if tails[mid] < n:
                lo = mid + 1
            else:
                hi = mid
        if lo == len(tails):
            #> Longer than anything so far, so the answer grows.
            tails.append(n)
        else:
            #> Otherwise improve an existing length's ending value.
            tails[lo] = n
    #> tails isn't the actual subsequence, but its length is the right answer.
    return len(tails)


APPROACHES = [
    {"id": "quadratic", "label": "Longest run ending here", "fn": quadratic,
     "complexity": {"time": "O(n²)", "space": "O(n)"},
     "viz": {"nums": "array", "best": "array", "i": "pointer:nums", "j": "pointer:nums"}},
    {"id": "patience", "label": "Patience with binary search", "fn": patience,
     "complexity": {"time": "O(n log n)", "space": "O(n)"},
     "viz": {"nums": "array", "tails": "array"}},
]
