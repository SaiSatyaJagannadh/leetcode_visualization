META = {
    "slug": "permutations",
    "title": "Permutations",
    "pattern": "Backtracking",
    "difficulty": "Medium",
    "leetcode": 46,
    "prompt": "Given distinct integers, return every possible ordering of them.",
    "examples": [
        {"input": "nums = [1,2,3]", "output": "[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]"},
        {"input": "nums = [1]", "output": "[[1]]"},
    ],
    "constraints": ["1 <= len(nums) <= 6", "All values distinct"],
    "unordered": True,
}

VARIANTS = [
    {"id": "typical", "label": "Three values", "input": {"nums": [1, 2, 3]}},
    {"id": "edge", "label": "One value", "input": {"nums": [1]}},
    {"id": "worst-case", "label": "Four values", "input": {"nums": [1, 2, 3, 4]}},
]


def backtrack(nums, current=None, used=None, out=None):
    if current is None:
        current, used, out = [], {}, []
    if len(current) == len(nums):
        #> Every position filled, so this ordering is complete.
        out.append(list(current))
        return out
    for i in range(len(nums)):
        #> Unlike subsets, order matters here, so we scan from 0 every time and
        #> use `used` to avoid placing the same element twice.
        if i in used:
            continue
        used[i] = True
        current.append(nums[i])
        backtrack(nums, current, used, out)
        #> Undo both marks together or later branches inherit a stale state.
        current.pop()
        del used[i]
    return out


APPROACHES = [
    {"id": "backtrack", "label": "Backtracking", "fn": backtrack,
     "complexity": {"time": "O(n · n!)", "space": "O(n)"},
     "viz": {"nums": "array", "current": "stack", "used": "map", "$calls": "recursion"}},
]
