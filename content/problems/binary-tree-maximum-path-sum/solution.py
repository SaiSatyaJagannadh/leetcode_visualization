from structs import build_tree

META = {
    "slug": "binary-tree-maximum-path-sum",
    "title": "Binary Tree Maximum Path Sum",
    "pattern": "Trees",
    "difficulty": "Hard",
    "leetcode": 124,
    "prompt": "A path is any sequence of connected nodes, using each node at most once, and need not pass through the root. Return the largest sum any path can reach.",
    "examples": [
        {"input": "root = [1,2,3]", "output": "6", "why": "2 → 1 → 3."},
        {"input": "root = [-10,9,20,null,null,15,7]", "output": "42",
         "why": "15 → 20 → 7 beats anything that climbs through the negative root."},
    ],
    "constraints": ["1 <= number of nodes <= 3 * 10^4", "Values may be negative"],
}

VARIANTS = [
    {"id": "typical", "label": "Through the root", "input": lambda: {"root": build_tree([1, 2, 3])}},
    {"id": "edge", "label": "Avoids the root", "input": lambda: {"root": build_tree([-10, 9, 20, None, None, 15, 7])}},
    {"id": "worst-case", "label": "All negative", "input": lambda: {"root": build_tree([-3, -2, -1])}},
]

BEST = [0]


def max_path(root):
    BEST[0] = root.val
    _walk(root)
    return BEST[0]


def _walk(node):
    if node is None:
        return 0
    #> A branch that sums to less than nothing is worse than not going that way,
    #> so clamp at zero rather than dragging the total down.
    left = max(_walk(node.left), 0)
    right = max(_walk(node.right), 0)
    #> The best path *bending* here uses both branches plus this node.
    if node.val + left + right > BEST[0]:
        BEST[0] = node.val + left + right
    #> What we return must be usable by our parent, so it can only go straight up
    #> through one branch — a bend can't be extended any further.
    return node.val + max(left, right)


APPROACHES = [
    {"id": "bend", "label": "Best bend at every node", "fn": max_path,
     "complexity": {"time": "O(n)", "space": "O(h)"},
     "viz": {"root": "node", "$calls": "recursion"}},
]
