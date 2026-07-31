from structs import build_tree

META = {
    "slug": "validate-binary-search-tree",
    "title": "Validate Binary Search Tree",
    "pattern": "Trees",
    "difficulty": "Medium",
    "leetcode": 98,
    "prompt": "Decide whether a binary tree is a valid search tree: every value in a node's left subtree is smaller than it, every value on the right is larger, all the way down.",
    "examples": [
        {"input": "root = [2,1,3]", "output": "true"},
        {"input": "root = [5,1,4,null,null,3,6]", "output": "false",
         "why": "3 sits in 5's right subtree but is smaller than 5, even though it beats its own parent."},
    ],
    "constraints": ["1 <= number of nodes <= 10^4"],
}

VARIANTS = [
    {"id": "typical", "label": "Valid", "input": lambda: {"root": build_tree([2, 1, 3])}},
    {"id": "edge", "label": "Fails against a grandparent", "input": lambda: {"root": build_tree([5, 1, 4, None, None, 3, 6])}},
    {"id": "worst-case", "label": "Valid and deep", "input": lambda: {"root": build_tree([8, 3, 10, 1, 6, None, 14])}},
]

LOW = -(10 ** 9)
HIGH = 10 ** 9


def bounded(root):
    #> Comparing a node only against its parent is the classic wrong answer: it
    #> misses values that violate an ancestor further up. Carrying a legal range
    #> down the tree is what catches those.
    return _check(root, LOW, HIGH)


def _check(node, low, high):
    if node is None:
        return True  #> An empty subtree can't break anything.
    if not (low < node.val < high):
        #> Outside the window its ancestors permit.
        return False
    #> Going left tightens the ceiling to this node; going right raises the floor.
    return _check(node.left, low, node.val) and _check(node.right, node.val, high)


ORDER = []


def inorder_is_sorted(root):
    #> A different characterisation entirely: a tree is a BST exactly when its
    #> in-order walk comes out strictly increasing. No bounds to carry, because
    #> the ordering constraint has been turned into a sequence check.
    ORDER.clear()
    _walk(root)
    for i in range(1, len(ORDER)):
        #> Strictly increasing — equal values are not allowed in a BST here.
        if ORDER[i] <= ORDER[i - 1]:
            return False
    return True


def _walk(node):
    if node is None:
        return
    #> Left, self, right. That order is what makes the output sorted when the
    #> tree is valid, and out of order the moment it is not.
    _walk(node.left)
    ORDER.append(node.val)
    _walk(node.right)


APPROACHES = [
    {"id": "inorder", "label": "In-order must be increasing", "fn": inorder_is_sorted,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"root": "node", "ORDER": "array", "$calls": "recursion"}},
    {"id": "bounds", "label": "Carry a legal range down", "fn": bounded,
     "complexity": {"time": "O(n)", "space": "O(h)"},
     "viz": {"root": "node", "$calls": "recursion"}},
]
