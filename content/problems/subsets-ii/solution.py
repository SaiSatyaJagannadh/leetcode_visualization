META = {
    "slug": "subsets-ii",
    "title": "Subsets II",
    "pattern": "Backtracking",
    "difficulty": "Medium",
    "leetcode": 90,
    "prompt": "Return every distinct subset of an array that may contain duplicates. Two subsets holding the same values count as one.",
    "examples": [
        {"input": "nums = [1,2,2]", "output": "[[],[1],[1,2],[1,2,2],[2],[2,2]]"},
        {"input": "nums = [0]", "output": "[[],[0]]"},
    ],
    "constraints": ["1 <= len(nums) <= 10"],
    "unordered": True,
}

VARIANTS = [
    {"id": "typical", "label": "One duplicate", "input": {"nums": [1, 2, 2]}},
    {"id": "edge", "label": "No duplicates", "input": {"nums": [1, 2]}},
    {"id": "worst-case", "label": "All identical", "input": {"nums": [2, 2, 2]}},
]


def backtrack(nums, start=0, current=None, out=None):
    if current is None:
        #> Sorting puts equal values side by side, which is what makes the
        #> duplicate check below a simple neighbour comparison.
        nums = sorted(nums)
        current, out = [], []
    out.append(list(current))
    for i in range(start, len(nums)):
        #> Skip a repeated value at the *same depth*. The first copy already
        #> generated every subset this one could, so a second is a duplicate.
        #> The i > start guard is essential: it still allows [2,2] to be built.
        if i > start and nums[i] == nums[i - 1]:
            continue
        current.append(nums[i])
        backtrack(nums, i + 1, current, out)
        current.pop()
    return out


def count_each_value(nums):
    #> Group equal values first, then decide how MANY of each to take rather
    #> than which positions. Duplicates cannot arise, so no skip rule is needed —
    #> the shape of the recursion rules them out instead of a guard.
    ordered = sorted(nums)
    groups = []
    for v in ordered:
        if groups and groups[-1][0] == v:
            groups[-1][1] += 1
        else:
            groups.append([v, 1])
    out = []
    _choose(groups, 0, [], out)
    return out


def _choose(groups, i, current, out):
    if i == len(groups):
        out.append(list(current))
        return
    value, most = groups[i][0], groups[i][1]
    for take in range(most + 1):
        #> Take 0, 1, ... up to every copy of this value, then move on.
        for _ in range(take):
            current.append(value)
        _choose(groups, i + 1, current, out)
        for _ in range(take):
            current.pop()


APPROACHES = [
    {"id": "counts", "label": "Choose how many of each", "fn": count_each_value,
     "complexity": {"time": "O(2\u207f)", "space": "O(n)"},
     "viz": {"ordered": "array", "groups": "array", "current": "stack", "out": "queue", "$calls": "recursion"}},
    {"id": "backtrack", "label": "Sort, then skip repeats", "fn": backtrack,
     "complexity": {"time": "O(n · 2ⁿ)", "space": "O(n)"},
     "viz": {"nums": "array", "current": "stack", "out": "queue", "$calls": "recursion"}},
]
