from structs import build_tree

META = {
    "slug": "maximum-depth-of-binary-tree",
    "title": "Maximum Depth of Binary Tree",
    "pattern": "Trees",
    "difficulty": "Easy",
    "leetcode": 104,
    "prompt": (
        "The depth of a binary tree is the number of nodes on the longest path "
        "from the root down to any leaf. Given the root, return that depth."
    ),
    "examples": [
        {"input": "root = [3,9,20,null,null,15,7]", "output": "3",
         "why": "The path 3 → 20 → 15 visits three nodes; no path is longer."},
        {"input": "root = []", "output": "0", "why": "No nodes, no depth."},
    ],
    "constraints": ["0 <= number of nodes <= 10^4", "-100 <= node value <= 100"],
}

VARIANTS = [
    {"id": "typical", "label": "Balanced", "input": lambda: {"root": build_tree([3, 9, 20, None, None, 15, 7])}},
    {"id": "edge", "label": "Single node", "input": lambda: {"root": build_tree([1])}},
    {
        "id": "worst-case",
        "label": "Right spine",
        "input": lambda: {"root": build_tree([1, None, 2, None, 3, None, 4])},
    },
]


def recursive(root):
    if root is None:
        #> An empty branch contributes no depth. This is what stops the recursion.
        return 0
    #> Ask each side how deep it is, then add one for the node standing here.
    left = recursive(root.left)
    right = recursive(root.right)
    #> Only the deeper side matters — depth is the longest path, not the total.
    return 1 + max(left, right)


def level_order(root):
    if root is None:
        return 0
    #> Walk the tree one full level at a time; the number of levels is the depth.
    level = [root]
    depth = 0
    while level:
        depth += 1  #> Every node in `level` sits at exactly this depth.
        nxt = []
        for node in level:
            #> Collect the children, which together form the next level down.
            if node.left is not None:
                nxt.append(node.left)
            if node.right is not None:
                nxt.append(node.right)
        level = nxt
    #> The last level had no children, so the loop ended at the deepest row.
    return depth


APPROACHES = [
    {
        "id": "recursive",
        "label": "Depth-first",
        "fn": recursive,
        "complexity": {"time": "O(n)", "space": "O(h)"},
        "viz": {"root": "node", "$calls": "recursion"},
    },
    {
        "id": "level-order",
        "label": "Level by level",
        "fn": level_order,
        "complexity": {"time": "O(n)", "space": "O(n)"},
        "viz": {"root": "node", "level": "queue", "nxt": "queue", "node": "node"},
    },
]
