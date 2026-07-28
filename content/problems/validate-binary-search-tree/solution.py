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


APPROACHES = [
    {"id": "bounds", "label": "Carry a legal range down", "fn": bounded,
     "complexity": {"time": "O(n)", "space": "O(h)"},
     "viz": {"root": "node", "$calls": "recursion"}},
]
