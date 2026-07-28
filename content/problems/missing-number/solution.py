META = {
    "slug": "missing-number",
    "title": "Missing Number",
    "pattern": "Bit Manipulation",
    "difficulty": "Easy",
    "leetcode": 268,
    "prompt": "An array holds n distinct values drawn from 0 to n. Return the one value that isn't there.",
    "examples": [
        {"input": "nums = [3,0,1]", "output": "2"},
        {"input": "nums = [0,1]", "output": "2", "why": "The missing value can be n itself."},
    ],
    "constraints": ["1 <= n <= 10^4", "All values distinct"],
}

VARIANTS = [
    {"id": "typical", "label": "Missing in the middle", "input": {"nums": [3, 0, 1]}},
    {"id": "edge", "label": "Missing the largest", "input": {"nums": [0, 1]}},
    {"id": "worst-case", "label": "Missing zero", "input": {"nums": [1, 2, 3]}},
]


def by_sum(nums):
    #> The full range has a known total, so the gap is whatever the array lacks.
    n = len(nums)
    expected = n * (n + 1) // 2
    actual = 0
    for v in nums:
        actual += v
    return expected - actual


def by_xor(nums):
    #> XOR each index against each value. Every number present pairs off with its
    #> own index and cancels; the missing one has an index with no partner, so it
    #> survives. Unlike the sum, this can never overflow.
    result = len(nums)
    for i in range(len(nums)):
        result = result ^ i ^ nums[i]
    return result


APPROACHES = [
    {"id": "sum", "label": "Compare against the expected sum", "fn": by_sum,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"nums": "array"}},
    {"id": "xor", "label": "XOR indices against values", "fn": by_xor,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"nums": "array", "i": "pointer:nums"}},
]
