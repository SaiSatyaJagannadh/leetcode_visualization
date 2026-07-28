META = {
    "slug": "combination-sum-ii",
    "title": "Combination Sum II",
    "pattern": "Backtracking",
    "difficulty": "Medium",
    "leetcode": 40,
    "prompt": "Candidates may repeat in the input, but each entry may be used at most once. List every distinct combination that reaches the target.",
    "examples": [
        {"input": "candidates = [10,1,2,7,6,1,5], target = 8", "output": "[[1,1,6],[1,2,5],[1,7],[2,6]]"},
        {"input": "candidates = [2,5,2,1,2], target = 5", "output": "[[1,2,2],[5]]"},
    ],
    "constraints": ["1 <= len(candidates) <= 100"],
    "unordered": True,
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"candidates": [10, 1, 2, 7, 6, 1, 5], "target": 8}},
    {"id": "edge", "label": "No solution", "input": {"candidates": [3, 3], "target": 5}},
    {"id": "worst-case", "label": "Many repeats", "input": {"candidates": [2, 5, 2, 1, 2], "target": 5}},
]


def backtrack(candidates, target, start=0, current=None, out=None):
    if current is None:
        candidates = sorted(candidates)
        current, out = [], []
    if target == 0:
        out.append(list(current))
        return out
    for i in range(start, len(candidates)):
        #> Same-depth duplicate: the earlier copy already explored this branch.
        if i > start and candidates[i] == candidates[i - 1]:
            continue
        if candidates[i] > target:
            #> Sorted, so this and everything after it overshoots. Stop entirely.
            break
        current.append(candidates[i])
        #> i + 1, not i: each entry is available only once.
        backtrack(candidates, target - candidates[i], i + 1, current, out)
        current.pop()
    return out


APPROACHES = [
    {"id": "backtrack", "label": "Sort, skip repeats, advance", "fn": backtrack,
     "complexity": {"time": "O(2ⁿ)", "space": "O(n)"},
     "viz": {"candidates": "array", "current": "stack", "out": "queue", "$calls": "recursion"}},
]
