from structs import build_tree

META = {
    "slug": "same-tree",
    "title": "Same Tree",
    "pattern": "Trees",
    "difficulty": "Easy",
    "leetcode": 100,
    "prompt": "Decide whether two binary trees have exactly the same shape and the same values in the same positions.",
    "examples": [
        {"input": "p = [1,2,3], q = [1,2,3]", "output": "true"},
        {"input": "p = [1,2], q = [1,null,2]", "output": "false",
         "why": "Same values, but one hangs left and the other right."},
    ],
    "constraints": ["0 <= number of nodes <= 100"],
}

VARIANTS = [
    {"id": "typical", "label": "Identical", "input": lambda: {"p": build_tree([1, 2, 3]), "q": build_tree([1, 2, 3])}},
    {"id": "edge", "label": "Different shape", "input": lambda: {"p": build_tree([1, 2]), "q": build_tree([1, None, 2])}},
    {"id": "worst-case", "label": "Differ deep down", "input": lambda: {"p": build_tree([1, 2, 3, 4]), "q": build_tree([1, 2, 3, 5])}},
]


def recursive(p, q):
    if p is None and q is None:
        #> Both ran out at the same place, which is agreement, not a mismatch.
        return True
    if p is None or q is None:
        #> Only one ran out, so the shapes already differ.
        return False
    if p.val != q.val:
        return False
    #> Same value here; the trees match only if both subtrees also match.
    return recursive(p.left, q.left) and recursive(p.right, q.right)


def serialise_and_compare(p, q):
    #> Flatten each tree to a string and compare the two. The null markers are
    #> what make it sound: without them, different shapes can flatten to the
    #> same sequence of values.
    return _spell(p) == _spell(q)


def _spell(node):
    if node is None:
        #> An explicit marker for "nothing here" — this is the whole trick.
        return "#"
    #> Root first, then both sides, so position is encoded as well as value.
    return "(" + str(node.val) + _spell(node.left) + _spell(node.right) + ")"


APPROACHES = [
    {"id": "serialise", "label": "Flatten both and compare", "fn": serialise_and_compare,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"p": "node", "q": "node", "$calls": "recursion"}},
    {"id": "recursive", "label": "Walk both at once", "fn": recursive,
     "complexity": {"time": "O(n)", "space": "O(h)"},
     "viz": {"p": "node", "q": "node", "$calls": "recursion"}},
]
