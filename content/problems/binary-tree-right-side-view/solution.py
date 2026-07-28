from structs import build_tree

META = {
    "slug": "binary-tree-right-side-view",
    "title": "Binary Tree Right Side View",
    "pattern": "Trees",
    "difficulty": "Medium",
    "leetcode": 199,
    "prompt": "Standing to the right of the tree, list the node values you can see, top to bottom — the rightmost node on each level.",
    "examples": [
        {"input": "root = [1,2,3,null,5,null,4]", "output": "[1,3,4]"},
        {"input": "root = [1,null,3]", "output": "[1,3]"},
    ],
    "constraints": ["0 <= number of nodes <= 100"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": lambda: {"root": build_tree([1, 2, 3, None, 5, None, 4])}},
    {"id": "edge", "label": "Left-only tree", "input": lambda: {"root": build_tree([1, 2, None, 3])}},
    {"id": "worst-case", "label": "Deep left branch", "input": lambda: {"root": build_tree([1, 2, 3, 4, None, None, None, 5])}},
]


def rightmost_per_level(root):
    if root is None:
        return []
    out = []
    level = [root]
    while level:
        #> The last node of a left-to-right level is the one visible from the right.
        #> Note it can come from a *left* subtree when the right side is shorter.
        out.append(level[-1].val)
        nxt = []
        for node in level:
            if node.left is not None:
                nxt.append(node.left)
            if node.right is not None:
                nxt.append(node.right)
        level = nxt
    return out


APPROACHES = [
    {"id": "levels", "label": "Last node of each level", "fn": rightmost_per_level,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"root": "node", "level": "queue", "nxt": "queue", "out": "queue", "node": "node"}},
]
