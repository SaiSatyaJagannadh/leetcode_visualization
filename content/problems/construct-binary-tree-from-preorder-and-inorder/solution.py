from structs import TreeNode, layout_tree

META = {
    "slug": "construct-binary-tree-from-preorder-and-inorder",
    "title": "Construct Binary Tree From Preorder and Inorder",
    "pattern": "Trees",
    "difficulty": "Medium",
    "leetcode": 105,
    "prompt": "Rebuild a binary tree from its preorder and inorder traversals. All values are distinct.",
    "examples": [
        {"input": "preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]", "output": "[3,9,20,null,null,15,7]"},
        {"input": "preorder = [-1], inorder = [-1]", "output": "[-1]"},
    ],
    "constraints": ["1 <= number of nodes <= 3000", "All values distinct"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"pre": [3, 9, 20, 15, 7], "ino": [9, 3, 15, 20, 7]}},
    {"id": "edge", "label": "Single node", "input": {"pre": [-1], "ino": [-1]}},
    {"id": "worst-case", "label": "Left spine", "input": {"pre": [1, 2, 3], "ino": [3, 2, 1]}},
]


def build(pre, ino):
    #> Preorder hands over roots in the order we need them; inorder tells us how
    #> many nodes fall on each side of a root. Together that pins the shape down.
    root = _make(pre, 0, ino, 0, len(ino) - 1)
    layout_tree(root)
    #> Level order, the same shape the examples use.
    out, level = [], [root]
    while any(n is not None for n in level):
        nxt = []
        for n in level:
            out.append(None if n is None else n.val)
            nxt.extend([None, None] if n is None else [n.left, n.right])
        level = nxt
    while out and out[-1] is None:
        out.pop()
    return out


def _make(pre, pi, ino, lo, hi):
    if lo > hi or pi >= len(pre):
        return None
    #> The next unused preorder value is this subtree's root, always.
    node = TreeNode(pre[pi])
    #> Find it in the inorder list: everything left of it is the left subtree.
    split = lo
    while ino[split] != pre[pi]:
        split += 1
    left_size = split - lo
    node.left = _make(pre, pi + 1, ino, lo, split - 1)
    #> Skip past the whole left subtree to reach the right subtree's root.
    node.right = _make(pre, pi + 1 + left_size, ino, split + 1, hi)
    return node


def build_with_index(pre, ino):
    #> Same reconstruction, but the position of each value in the inorder list is
    #> looked up instead of searched for. The scan version walks the inorder list
    #> once per node, which is what makes it quadratic on a skewed tree.
    where = {}
    for i in range(len(ino)):
        #> Values are distinct, so one map answers every split in constant time.
        where[ino[i]] = i
    cursor = [0]
    root = _fast(pre, ino, where, cursor, 0, len(ino) - 1)
    if root is not None:
        layout_tree(root)
    out, level = [], [root]
    while any(n is not None for n in level):
        nxt = []
        for n in level:
            out.append(None if n is None else n.val)
            nxt.extend([None, None] if n is None else [n.left, n.right])
        level = nxt
    while out and out[-1] is None:
        out.pop()
    return out


def _fast(pre, ino, where, cursor, lo, hi):
    if lo > hi:
        return None
    #> A shared cursor walks preorder forwards, so no index arithmetic is needed
    #> to skip past a left subtree — it has already consumed exactly its own nodes.
    node = TreeNode(pre[cursor[0]])
    split = where[pre[cursor[0]]]
    cursor[0] += 1
    node.left = _fast(pre, ino, where, cursor, lo, split - 1)
    node.right = _fast(pre, ino, where, cursor, split + 1, hi)
    return node


APPROACHES = [
    {"id": "indexed", "label": "Look the split up, don't scan", "fn": build_with_index,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"pre": "array", "ino": "array", "where": "map", "$calls": "recursion"}},
    {"id": "split", "label": "Split on the inorder index", "fn": build,
     "complexity": {"time": "O(n²)", "space": "O(n)"},
     "viz": {"pre": "array", "ino": "array", "root": "node", "$calls": "recursion"}},
]
