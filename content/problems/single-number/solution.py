META = {
    "slug": "single-number",
    "title": "Single Number",
    "pattern": "Bit Manipulation",
    "difficulty": "Easy",
    "leetcode": 136,
    "prompt": "Every value appears twice except one. Find the loner using constant space and a single pass.",
    "examples": [
        {"input": "nums = [4,1,2,1,2]", "output": "4"},
        {"input": "nums = [2,2,1]", "output": "1"},
    ],
    "constraints": ["1 <= len(nums) <= 3 * 10^4", "Exactly one value is unpaired"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"nums": [4, 1, 2, 1, 2]}},
    {"id": "edge", "label": "Single element", "input": {"nums": [7]}},
    {"id": "worst-case", "label": "Loner last", "input": {"nums": [1, 1, 2, 2, 9]}},
]


def with_counts(nums):
    #> Correct, but the tally is extra space the problem rules out.
    counts = {}
    for n in nums:
        counts[n] = counts.get(n, 0) + 1
    for n in counts:
        if counts[n] == 1:
            return n
    return -1


def xor_everything(nums):
    #> XOR cancels a value against itself and leaves anything else untouched, so
    #> folding it over the whole array erases every pair. Order doesn't matter,
    #> which is why the pairs need not be adjacent.
    result = 0
    for n in nums:
        result = result ^ n
    return result


APPROACHES = [
    {"id": "counts", "label": "Count occurrences", "fn": with_counts,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"nums": "array", "counts": "map"}},
    {"id": "xor", "label": "XOR everything", "fn": xor_everything,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"nums": "array"}},
]
