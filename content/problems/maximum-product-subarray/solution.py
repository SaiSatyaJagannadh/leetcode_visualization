META = {
    "slug": "maximum-product-subarray",
    "title": "Maximum Product Subarray",
    "pattern": "1-D Dynamic Programming",
    "difficulty": "Medium",
    "leetcode": 152,
    "prompt": "Find the contiguous run of numbers with the largest product and return that product.",
    "examples": [
        {"input": "nums = [2,3,-2,4]", "output": "6", "why": "The run [2,3]."},
        {"input": "nums = [-2,0,-1]", "output": "0"},
    ],
    "constraints": ["1 <= len(nums) <= 2 * 10^4"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"nums": [2, 3, -2, 4]}},
    {"id": "edge", "label": "Zero resets", "input": {"nums": [-2, 0, -1]}},
    {"id": "worst-case", "label": "Two negatives", "input": {"nums": [-2, 3, -4]}},
]


def track_both_ends(nums):
    #> Unlike sums, a very *negative* running product is valuable: one more
    #> negative number flips it into a large positive. So track both extremes.
    best = nums[0]
    high = nums[0]
    low = nums[0]
    for i in range(1, len(nums)):
        n = nums[i]
        #> A negative n swaps the roles of high and low, which is exactly why
        #> both have to be recomputed from the old pair at once.
        candidates = [n, high * n, low * n]
        high = max(candidates)
        low = min(candidates)
        if high > best:
            best = high
    return best


def every_run(nums):
    #> Multiply out every run and keep the largest. No cleverness about signs is
    #> needed because nothing is being carried forward — which is exactly why it
    #> costs a factor of n more than tracking the two extremes.
    best = nums[0]
    for i in range(len(nums)):
        product = 1
        for j in range(i, len(nums)):
            #> Extend the run starting at i one number at a time.
            product *= nums[j]
            if product > best:
                best = product
    return best


APPROACHES = [
    {"id": "brute-force", "label": "Multiply out every run", "fn": every_run,
     "complexity": {"time": "O(n\u00b2)", "space": "O(1)"},
     "viz": {"nums": "array", "i": "pointer:nums", "j": "pointer:nums"}},
    {"id": "both-ends", "label": "Track the highest and lowest", "fn": track_both_ends,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"nums": "array", "i": "pointer:nums", "candidates": "array"}},
]
