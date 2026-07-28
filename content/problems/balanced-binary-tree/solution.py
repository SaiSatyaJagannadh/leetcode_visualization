from structs import build_tree

META = {
    "slug": "balanced-binary-tree",
    "title": "Balanced Binary Tree",
    "pattern": "Trees",
    "difficulty": "Easy",
    "leetcode": 110,
    "prompt": "A tree is height-balanced when, at every node, the two subtree heights differ by at most one. Decide whether the given tree qualifies.",
    "examples": [
        {"input": "root = [3,9,20,null,null,15,7]", "output": "true"},
        {"input": "root = [1,2,2,3,3,null,null,4,4]", "output": "false"},
    ],
    "constraints": ["0 <= number of nodes <= 5000"],
}

VARIANTS = [
    {"id": "typical", "label": "Balanced", "input": lambda: {"root": build_tree([3, 9, 20, None, None, 15, 7])}},
    {"id": "edge", "label": "Unbalanced", "input": lambda: {"root": build_tree([1, 2, 2, 3, 3, None, None, 4])}},
    {"id": "worst-case", "label": "Spine", "input": lambda: {"root": build_tree([1, 2, None, 3])}},
]


def height_or_fail(root):
    #> Returning -1 as a poison value means one pass answers both questions:
    #> how tall is this subtree, and did anything below it already fail?
    return _check(root) != -1


def _check(node):
    if node is None:
        return 0
    left = _check(node.left)
    if left == -1:
        return -1  #> Already broken below; stop measuring and propagate.
    right = _check(node.right)
    if right == -1:
        return -1
    if abs(left - right) > 1:
        #> This node itself is the imbalance.
        return -1
    return 1 + max(left, right)


APPROACHES = [
    {"id": "poison", "label": "Height, or -1 for failed", "fn": height_or_fail,
     "complexity": {"time": "O(n)", "space": "O(h)"},
     "viz": {"root": "node", "$calls": "recursion"}},
]
