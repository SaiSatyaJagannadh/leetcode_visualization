from structs import build_tree

META = {
    "slug": "lowest-common-ancestor-of-a-bst",
    "title": "Lowest Common Ancestor of a BST",
    "pattern": "Trees",
    "difficulty": "Medium",
    "leetcode": 235,
    "prompt": "In a binary search tree, find the deepest node that has both given values somewhere beneath it. A node counts as its own descendant.",
    "examples": [
        {"input": "root = [6,2,8,0,4,7,9], p = 2, q = 8", "output": "6"},
        {"input": "root = [6,2,8,0,4,7,9], p = 2, q = 4", "output": "2",
         "why": "A node can be the ancestor of itself."},
    ],
    "constraints": ["Both values exist in the tree", "All values are distinct"],
}

TREE = [6, 2, 8, 0, 4, 7, 9]

VARIANTS = [
    {"id": "typical", "label": "Split at the root", "input": lambda: {"root": build_tree(TREE), "p": 2, "q": 8}},
    {"id": "edge", "label": "One is the ancestor", "input": lambda: {"root": build_tree(TREE), "p": 2, "q": 4}},
    {"id": "worst-case", "label": "Deep on one side", "input": lambda: {"root": build_tree(TREE), "p": 7, "q": 9}},
]


def walk_down(root, p, q):
    node = root
    while node is not None:
        #> Both targets smaller than this node means both live to the left, so
        #> this node can't be the *lowest* common ancestor. Same logic mirrored.
        if p < node.val and q < node.val:
            node = node.left
        elif p > node.val and q > node.val:
            node = node.right
        else:
            #> The targets straddle this node, or one of them is this node. Either
            #> way, one step further down would lose one of them — so stop here.
            return node.val
    return None


def paths_from_root(root, p, q):
    #> Works on any binary tree, not just a BST: record the route to each target,
    #> then compare. The BST walk needs neither list because the ordering tells
    #> it which way to go without ever searching.
    a = []
    b = []
    _path(root, p, a)
    _path(root, q, b)
    last = None
    for i in range(min(len(a), len(b))):
        if a[i] != b[i]:
            #> The routes have diverged, so the previous shared node is the answer.
            break
        last = a[i]
    return last


def _path(node, target, out):
    if node is None:
        return False
    out.append(node.val)
    if node.val == target:
        return True
    if _path(node.left, target, out) or _path(node.right, target, out):
        return True
    #> Dead end, so this node is not on the route after all.
    out.pop()
    return False


APPROACHES = [
    {"id": "paths", "label": "Compare the two routes", "fn": paths_from_root,
     "complexity": {"time": "O(n)", "space": "O(h)"},
     "viz": {"root": "node", "a": "queue", "b": "queue", "$calls": "recursion"}},
    {"id": "walk", "label": "Walk down until they split", "fn": walk_down,
     "complexity": {"time": "O(h)", "space": "O(1)"},
     "viz": {"root": "node", "node": "node"}},
]
