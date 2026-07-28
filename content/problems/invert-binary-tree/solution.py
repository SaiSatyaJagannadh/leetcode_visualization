from structs import build_tree, layout_tree

META = {
    "slug": "invert-binary-tree",
    "title": "Invert Binary Tree",
    "pattern": "Trees",
    "difficulty": "Easy",
    "leetcode": 226,
    "prompt": "Mirror a binary tree: every node's left and right subtrees swap places, all the way down.",
    "examples": [
        {"input": "root = [4,2,7,1,3,6,9]", "output": "[4,7,2,9,6,3,1]"},
        {"input": "root = []", "output": "[]"},
    ],
    "constraints": ["0 <= number of nodes <= 100"],
}

VARIANTS = [
    {"id": "typical", "label": "Full tree", "input": lambda: {"root": build_tree([4, 2, 7, 1, 3, 6, 9])}},
    {"id": "edge", "label": "Single node", "input": lambda: {"root": build_tree([1])}},
    {"id": "worst-case", "label": "Left spine", "input": lambda: {"root": build_tree([1, 2, None, 3])}},
]


def recursive(root):
    if root is None:
        return None
    #> Swap this node's children, then let recursion handle both subtrees. Order
    #> doesn't matter here — swapping first or last gives the same mirror.
    root.left, root.right = root.right, root.left
    recursive(root.left)
    recursive(root.right)
    layout_tree(root)
    return root


def iterative(root):
    if root is None:
        return None
    #> A stack does the same walk without the call frames.
    stack = [root]
    while stack:
        node = stack.pop()
        node.left, node.right = node.right, node.left
        if node.left is not None:
            stack.append(node.left)
        if node.right is not None:
            stack.append(node.right)
    layout_tree(root)
    return root


APPROACHES = [
    {"id": "recursive", "label": "Recursive", "fn": recursive,
     "complexity": {"time": "O(n)", "space": "O(h)"},
     "viz": {"root": "node", "$calls": "recursion"}},
    {"id": "iterative", "label": "Explicit stack", "fn": iterative,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"root": "node", "node": "node"}},
]
