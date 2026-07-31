META = {
    "slug": "combination-sum",
    "title": "Combination Sum",
    "pattern": "Backtracking",
    "difficulty": "Medium",
    "leetcode": 39,
    "prompt": "Given distinct candidates and a target, list every combination summing to the target. A candidate may be reused any number of times, and two combinations differing only in order count as one.",
    "examples": [
        {"input": "candidates = [2,3,6,7], target = 7", "output": "[[2,2,3],[7]]"},
        {"input": "candidates = [2], target = 1", "output": "[]"},
    ],
    "constraints": ["1 <= len(candidates) <= 30", "All candidates distinct"],
    "unordered": True,
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"candidates": [2, 3, 6, 7], "target": 7}},
    {"id": "edge", "label": "No solution", "input": {"candidates": [2], "target": 1}},
    {"id": "worst-case", "label": "Many repeats", "input": {"candidates": [2, 3], "target": 8}},
]


def backtrack(candidates, target, start=0, current=None, out=None):
    if current is None:
        current, out = [], []
    if target == 0:
        #> Landed exactly on the target, so this branch is an answer.
        out.append(list(current))
        return out
    if target < 0:
        #> Overshot. Every candidate is positive, so nothing below can recover.
        return out
    for i in range(start, len(candidates)):
        current.append(candidates[i])
        #> Passing i, not i + 1, is what lets a candidate repeat. Never going
        #> backwards is what stops [2,3] and [3,2] both being found.
        backtrack(candidates, target - candidates[i], i, current, out)
        current.pop()  #> Undo, so the next candidate starts clean.
    return out


def take_or_skip(candidates, target, i=0, current=None, out=None):
    #> The same search asked as a yes/no question at each candidate instead of a
    #> loop over the remaining ones. Two branches, not n.
    if current is None:
        current, out = [], []
    if target == 0:
        out.append(list(current))
        return out
    if target < 0 or i >= len(candidates):
        #> Overshot, or ran out of candidates without landing on zero.
        return out
    #> Branch one: take this candidate and stay on it, so it can repeat.
    current.append(candidates[i])
    take_or_skip(candidates, target - candidates[i], i, current, out)
    current.pop()
    #> Branch two: give up on this candidate for good and move to the next.
    #> Never coming back is what stops [2,3] and [3,2] both being found.
    take_or_skip(candidates, target, i + 1, current, out)
    return out


APPROACHES = [
    {"id": "take-or-skip", "label": "Take it or leave it", "fn": take_or_skip,
     "complexity": {"time": "O(2^(t/m))", "space": "O(t/m)"},
     "viz": {"candidates": "array", "current": "stack", "out": "queue", "$calls": "recursion"}},
    {"id": "backtrack", "label": "Backtracking", "fn": backtrack,
     "complexity": {"time": "O(n^(t/m))", "space": "O(t/m)"},
     "viz": {"candidates": "array", "current": "stack", "out": "queue", "$calls": "recursion"}},
]
