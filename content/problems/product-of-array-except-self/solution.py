META = {
    "slug": "product-of-array-except-self",
    "title": "Product of Array Except Self",
    "pattern": "Arrays & Hashing",
    "difficulty": "Medium",
    "leetcode": 238,
    "prompt": "Return an array where each position holds the product of every number except the one at that position. Solve it without division.",
    "examples": [
        {"input": "nums = [1,2,3,4]", "output": "[24,12,8,6]",
         "why": "Position 0 is 2x3x4, position 1 is 1x3x4, and so on."},
        {"input": "nums = [-1,1,0,-3,3]", "output": "[0,0,9,0,0]",
         "why": "A single zero wipes out every position except its own."},
    ],
    "constraints": ["2 <= len(nums) <= 10^5", "The full product fits in a 32-bit integer"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"nums": [1, 2, 3, 4]}},
    {"id": "edge", "label": "Contains a zero", "input": {"nums": [-1, 1, 0, -3, 3]}},
    {"id": "worst-case", "label": "Two zeros", "input": {"nums": [0, 4, 0]}},
]


def brute_force(nums):
    out = []
    for i in range(len(nums)):
        product = 1
        for j in range(len(nums)):
            #> Multiply everything except the one position we're answering for.
            if j != i:
                product *= nums[j]
        out.append(product)
    return out


def prefix_suffix(nums):
    n = len(nums)
    out = [1] * n
    #> First pass: out[i] becomes the product of everything strictly to the left.
    running = 1
    for i in range(n):
        out[i] = running
        running *= nums[i]
    #> Second pass, walking back: multiply in the product of everything to the
    #> right. Left times right is the whole array except position i, no division.
    running = 1
    for i in range(n - 1, -1, -1):
        out[i] *= running
        running *= nums[i]
    return out


APPROACHES = [
    {"id": "brute-force", "label": "Recompute each", "fn": brute_force,
     "complexity": {"time": "O(n²)", "space": "O(1)"},
     "viz": {"nums": "array", "out": "array", "i": "pointer:nums", "j": "pointer:nums"}},
    {"id": "prefix-suffix", "label": "Prefix then suffix", "fn": prefix_suffix,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"nums": "array", "out": "array", "i": "pointer:out"}},
]
