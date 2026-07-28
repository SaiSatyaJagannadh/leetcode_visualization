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


APPROACHES = [
    {"id": "both-ends", "label": "Track the highest and lowest", "fn": track_both_ends,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"nums": "array", "i": "pointer:nums", "candidates": "array"}},
]
