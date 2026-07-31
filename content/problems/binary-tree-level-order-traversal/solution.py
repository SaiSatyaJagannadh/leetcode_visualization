from structs import build_tree

META = {
    "slug": "binary-tree-level-order-traversal",
    "title": "Binary Tree Level Order Traversal",
    "pattern": "Trees",
    "difficulty": "Medium",
    "leetcode": 102,
    "prompt": "Return the node values level by level, left to right, with each level as its own list.",
    "examples": [
        {"input": "root = [3,9,20,null,null,15,7]", "output": "[[3],[9,20],[15,7]]"},
        {"input": "root = []", "output": "[]"},
    ],
    "constraints": ["0 <= number of nodes <= 2000"],
}

VARIANTS = [
    {"id": "typical", "label": "Three levels", "input": lambda: {"root": build_tree([3, 9, 20, None, None, 15, 7])}},
    {"id": "edge", "label": "Single node", "input": lambda: {"root": build_tree([1])}},
    {"id": "worst-case", "label": "Right spine", "input": lambda: {"root": build_tree([1, None, 2, None, 3])}},
]


def by_level(root):
    if root is None:
        return []
    out = []
    #> Hold one entire level at a time rather than a running queue. That way the
    #> level boundaries are structural instead of something we have to count.
    level = [root]
    while level:
        values = []
        nxt = []
        for node in level:
            values.append(node.val)
            #> Children go left-then-right, which preserves the order one row down.
            if node.left is not None:
                nxt.append(node.left)
            if node.right is not None:
                nxt.append(node.right)
        out.append(values)
        level = nxt
    return out


ROWS = []


def by_depth(root):
    #> No queue: walk depth-first and let each node file itself under its depth.
    ROWS.clear()
    _visit(root, 0)
    return [row for row in ROWS]


def _visit(node, depth):
    if node is None:
        return
    if depth == len(ROWS):
        #> First time this deep, so this row does not exist yet.
        ROWS.append([])
    #> Left before right at every level, which is what keeps each row in order
    #> even though we arrive at the nodes in a completely different sequence.
    ROWS[depth].append(node.val)
    _visit(node.left, depth + 1)
    _visit(node.right, depth + 1)


APPROACHES = [
    {"id": "dfs-depth", "label": "Depth-first, filed by depth", "fn": by_depth,
     "complexity": {"time": "O(n)", "space": "O(h)"},
     "viz": {"root": "node", "ROWS": "array", "$calls": "recursion"}},
    {"id": "levels", "label": "One level at a time", "fn": by_level,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"root": "node", "level": "queue", "nxt": "queue", "node": "node", "values": "queue"}},
]
