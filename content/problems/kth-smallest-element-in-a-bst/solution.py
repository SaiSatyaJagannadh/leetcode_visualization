from structs import build_tree

META = {
    "slug": "kth-smallest-element-in-a-bst",
    "title": "Kth Smallest Element in a BST",
    "pattern": "Trees",
    "difficulty": "Medium",
    "leetcode": 230,
    "prompt": "Return the kth smallest value in a binary search tree, counting from one.",
    "examples": [
        {"input": "root = [3,1,4,null,2], k = 1", "output": "1"},
        {"input": "root = [5,3,6,2,4,null,null,1], k = 3", "output": "3"},
    ],
    "constraints": ["1 <= k <= number of nodes <= 10^4"],
}

TREE = [5, 3, 6, 2, 4, None, None, 1]

VARIANTS = [
    {"id": "typical", "label": "k = 3", "input": lambda: {"root": build_tree(TREE), "k": 3}},
    {"id": "edge", "label": "Smallest", "input": lambda: {"root": build_tree(TREE), "k": 1}},
    {"id": "worst-case", "label": "Largest", "input": lambda: {"root": build_tree(TREE), "k": 6}},
]


def inorder_walk(root, k):
    #> An in-order walk of a BST visits values in sorted order, so the kth node it
    #> reaches *is* the answer — no sorting and no full traversal required.
    stack = []
    node = root
    seen = 0
    while node is not None or stack:
        while node is not None:
            #> Dive as far left as possible; the deepest is the smallest unseen.
            stack.append(node)
            node = node.left
        node = stack.pop()
        seen += 1
        if seen == k:
            #> Stop the moment we arrive — everything beyond is larger.
            return node.val
        node = node.right
    return None


ORDER = []


def flatten_then_index(root, k):
    #> Ignore that it is a BST: collect every value, sort, take the kth. Correct
    #> for any tree, but it visits all n nodes when the in-order walk stops after
    #> k — and it sorts values that were already in order.
    ORDER.clear()
    _collect(root)
    ordered = sorted(ORDER)
    if k > len(ordered):
        return None
    return ordered[k - 1]


def _collect(node):
    if node is None:
        return
    ORDER.append(node.val)
    _collect(node.left)
    _collect(node.right)


APPROACHES = [
    {"id": "flatten", "label": "Collect everything, then sort", "fn": flatten_then_index,
     "complexity": {"time": "O(n log n)", "space": "O(n)"},
     "viz": {"root": "node", "ORDER": "array", "ordered": "array", "$calls": "recursion"}},
    {"id": "inorder", "label": "In-order until k", "fn": inorder_walk,
     "complexity": {"time": "O(h + k)", "space": "O(h)"},
     "viz": {"root": "node", "node": "node", "stack": "stack"}},
]
