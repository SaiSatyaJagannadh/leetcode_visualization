"""Depth 4+, siblings, a pruned branch, and backtrack-and-retry.

The most important fixture: the call tree has to grow, mark dead branches, and
carry the step each frame was entered so the renderer can jump to it.
"""

META = {"slug": "_recursion", "title": "Recursion renderer", "pattern": "Fixture"}

VARIANTS = [
    {"id": "typical", "label": "n = 5", "input": {"n": 5, "budget": 8}},
    {"id": "edge", "label": "Base case only", "input": {"n": 1, "budget": 8}},
]


def fib(n, budget):
    #> Two children per call, so the tree fans out and repeats work.
    if n <= 1:
        return n  #> Base case: a leaf, nothing below it.
    left = fib(n - 1, budget)  #> The first child runs to completion before its sibling starts.
    right = fib(n - 2, budget)  #> Its sibling picks up with everything the first one learned.
    return left + right


def bounded(n, budget):
    #> Same shape, but a branch that can't fit the budget dies immediately.
    if budget < 0:
        return 0  #> Pruned: this whole subtree is abandoned without exploring it.
    if n <= 1:
        return n
    return bounded(n - 1, budget - n) + bounded(n - 2, budget - n)


APPROACHES = [
    {
        "id": "fib",
        "label": "Naive fib",
        "fn": fib,
        "complexity": {"time": "O(2ⁿ)", "space": "O(n)"},
        "viz": {"$calls": "recursion"},
    },
    {
        "id": "bounded",
        "label": "Pruned search",
        "fn": bounded,
        "complexity": {"time": "O(2ⁿ)", "space": "O(n)"},
        "viz": {"$calls": "recursion"},
    },
]
