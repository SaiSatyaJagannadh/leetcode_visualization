META = {
    "slug": "subsets",
    "title": "Subsets",
    "pattern": "Backtracking",
    "difficulty": "Medium",
    "leetcode": 78,
    "prompt": (
        "Given an array of distinct integers, return every possible subset. The "
        "answer may be in any order, and it includes both the empty subset and "
        "the whole array."
    ),
    "examples": [
        {"input": "nums = [1,2,3]", "output": "[[],[1],[1,2],[1,2,3],[1,3],[2],[2,3],[3]]",
         "why": "Each of the three numbers is either in or out, giving 2³ = 8 subsets."},
        {"input": "nums = [0]", "output": "[[],[0]]"},
    ],
    "constraints": ["1 <= len(nums) <= 10", "All values are distinct"],
    "unordered": True,  # subsets may come back in any order
}

VARIANTS = [
    {"id": "typical", "label": "Three items", "input": {"nums": [1, 2, 3]}},
    {"id": "edge", "label": "One item", "input": {"nums": [7]}},
    {"id": "worst-case", "label": "Four items", "input": {"nums": [1, 2, 3, 4]}},
]


def backtrack(nums, start=0, current=None, out=None):
    if current is None:
        current, out = [], []
    #> Every node of this tree is a real subset, including the empty one at the root.
    out.append(list(current))
    for i in range(start, len(nums)):
        #> Choose: commit to nums[i] being in the subset.
        current.append(nums[i])
        #> Explore: build every subset that starts with what we've chosen so far.
        #> Passing i + 1 is what stops [1,2] and [2,1] from both being generated.
        backtrack(nums, i + 1, current, out)
        #> Un-choose: take it back out so the next sibling starts from a clean slate.
        current.pop()
    return out


def bitmask(nums, start=0, current=None, out=None):
    out = []
    #> Each number from 0 to 2ⁿ-1 is a different in-or-out answer for every element.
    for mask in range(2 ** len(nums)):
        subset = []
        for i in range(len(nums)):
            #> Bit i of the mask decides whether nums[i] joins this subset.
            if mask & (1 << i):
                subset.append(nums[i])
        out.append(subset)
    return out


APPROACHES = [
    {
        "id": "backtrack",
        "label": "Backtracking",
        "fn": backtrack,
        "complexity": {"time": "O(n · 2ⁿ)", "space": "O(n)"},
        "viz": {"nums": "array", "current": "stack", "i": "pointer:nums", "$calls": "recursion"},
    },
    {
        "id": "bitmask",
        "label": "Bitmask",
        "fn": bitmask,
        "complexity": {"time": "O(n · 2ⁿ)", "space": "O(1)"},
        "viz": {"nums": "array", "i": "pointer:nums", "subset": "stack"},
    },
]
