from structs import build_tree

META = {
    "slug": "subtree-of-another-tree",
    "title": "Subtree of Another Tree",
    "pattern": "Trees",
    "difficulty": "Easy",
    "leetcode": 572,
    "prompt": "Decide whether the second tree appears inside the first as a complete subtree — a node of the first tree plus all of its descendants matching exactly.",
    "examples": [
        {"input": "root = [3,4,5,1,2], subRoot = [4,1,2]", "output": "true"},
        {"input": "root = [3,4,5,1,2,null,null,null,null,0], subRoot = [4,1,2]", "output": "false",
         "why": "The match must include every descendant, and this one has an extra node."},
    ],
    "constraints": ["1 <= nodes in root <= 2000", "1 <= nodes in subRoot <= 1000"],
}

VARIANTS = [
    {"id": "typical", "label": "Present", "input": lambda: {"root": build_tree([3, 4, 5, 1, 2]), "sub": build_tree([4, 1, 2])}},
    {"id": "edge", "label": "Absent", "input": lambda: {"root": build_tree([3, 4, 5]), "sub": build_tree([4, 1])}},
    {"id": "worst-case", "label": "Whole tree", "input": lambda: {"root": build_tree([1, 2]), "sub": build_tree([1, 2])}},
]


def search_every_node(root, sub):
    if root is None:
        return False
    #> Try matching right here first.
    if _same(root, sub):
        return True
    #> Otherwise the match, if any, is entirely inside one of the subtrees.
    return search_every_node(root.left, sub) or search_every_node(root.right, sub)


def _same(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    if a.val != b.val:
        return False
    return _same(a.left, b.left) and _same(a.right, b.right)


def substring_of_serialised(root, sub):
    #> Flatten both trees, then ask whether one spelling contains the other.
    #> Turning a tree question into a string search — and the bracketing is what
    #> stops a partial subtree matching by accident.
    big = _spell(root)
    small = _spell(sub)
    return small in big


def _spell(node):
    if node is None:
        return "#"
    #> Brackets fence each subtree off, so a match inside `big` can only line up
    #> with a complete subtree rather than a fragment of one.
    return "(" + str(node.val) + _spell(node.left) + _spell(node.right) + ")"


APPROACHES = [
    {"id": "serialise", "label": "Substring of the flattened tree", "fn": substring_of_serialised,
     "complexity": {"time": "O(m + n)", "space": "O(m + n)"},
     "viz": {"root": "node", "sub": "node", "$calls": "recursion"}},
    {"id": "search", "label": "Try every node as the root", "fn": search_every_node,
     "complexity": {"time": "O(mn)", "space": "O(h)"},
     "viz": {"root": "node", "sub": "node", "$calls": "recursion"}},
]
