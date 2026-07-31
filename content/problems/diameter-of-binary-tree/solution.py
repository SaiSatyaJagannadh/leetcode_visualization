from structs import build_tree

META = {
    "slug": "diameter-of-binary-tree",
    "title": "Diameter of Binary Tree",
    "pattern": "Trees",
    "difficulty": "Easy",
    "leetcode": 543,
    "prompt": "The diameter is the number of edges on the longest path between any two nodes. That path need not pass through the root. Return it.",
    "examples": [
        {"input": "root = [1,2,3,4,5]", "output": "3", "why": "The path 4 → 2 → 1 → 3 crosses three edges."},
        {"input": "root = [1,2]", "output": "1"},
    ],
    "constraints": ["1 <= number of nodes <= 10^4"],
}

VARIANTS = [
    {"id": "typical", "label": "Through the root", "input": lambda: {"root": build_tree([1, 2, 3, 4, 5])}},
    {"id": "edge", "label": "Two nodes", "input": lambda: {"root": build_tree([1, 2])}},
    {"id": "worst-case", "label": "Misses the root", "input": lambda: {"root": build_tree([1, 2, None, 3, 4, 5, 6])}},
]

BEST = [0]


def depth_and_diameter(root):
    BEST[0] = 0
    _walk(root)
    return BEST[0]


def _walk(node):
    if node is None:
        return 0
    #> How deep each side goes, measured in edges.
    left = _walk(node.left)
    right = _walk(node.right)
    #> The longest path *bending* at this node uses both sides. Checking that at
    #> every node is what finds paths that never touch the root.
    if left + right > BEST[0]:
        BEST[0] = left + right
    #> But what we hand upward is a path going straight up, so only one side counts.
    return 1 + max(left, right)


def recompute_heights(root):
    #> Ask, at every node, how long a path bending here would be.
    return _widest(root)


def _widest(node):
    if node is None:
        return 0
    #> Both heights are computed from scratch, so every subtree is walked once
    #> per ancestor. That repetition is the whole difference from the one-pass.
    here = _height(node.left) + _height(node.right)
    best = here
    #> The best bend might be further down, so ask both children too.
    left = _widest(node.left)
    right = _widest(node.right)
    if left > best:
        best = left
    if right > best:
        best = right
    return best


def _height(node):
    if node is None:
        return 0
    return 1 + max(_height(node.left), _height(node.right))


APPROACHES = [
    {"id": "brute-force", "label": "Re-measure at every node", "fn": recompute_heights,
     "complexity": {"time": "O(n\u00b2)", "space": "O(h)"},
     "viz": {"root": "node", "$calls": "recursion"}},
    {"id": "one-pass", "label": "Depth, tracking the best bend", "fn": depth_and_diameter,
     "complexity": {"time": "O(n)", "space": "O(h)"},
     "viz": {"root": "node", "$calls": "recursion"}},
]
