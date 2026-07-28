from structs import TreeNode, build_tree, layout_tree

META = {
    "slug": "serialize-and-deserialize-binary-tree",
    "title": "Serialize and Deserialize Binary Tree",
    "pattern": "Trees",
    "difficulty": "Hard",
    "leetcode": 297,
    "prompt": "Turn a binary tree into a string, and turn that string back into the identical tree. The trace does both and checks the round trip.",
    "examples": [
        {"input": "root = [1,2,3,null,null,4,5]", "output": '"1,2,#,#,3,4,#,#,5,#,#"',
         "why": "Preorder with an explicit marker for every missing child."},
        {"input": "root = []", "output": '"#"'},
    ],
    "constraints": ["0 <= number of nodes <= 10^4", "Any encoding is allowed"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": lambda: {"root": build_tree([1, 2, 3, None, None, 4, 5])}},
    {"id": "edge", "label": "Single node", "input": lambda: {"root": build_tree([1])}},
    {"id": "worst-case", "label": "Right spine", "input": lambda: {"root": build_tree([1, None, 2, None, 3])}},
]

NULL = "#"


def round_trip(root):
    #> Writing a marker for every absent child is what makes the string
    #> unambiguous — without it, [1,2] and [1,null,2] would encode identically.
    parts = []
    _write(root, parts)
    text = ",".join(parts)

    #> Reading back is preorder again: take a token, and if it isn't the marker,
    #> its two children are whatever comes next. The cursor is shared state.
    cursor = [0]
    tokens = text.split(",")
    rebuilt = _read(tokens, cursor)
    if rebuilt is not None:
        layout_tree(rebuilt)
    return text


def _write(node, parts):
    if node is None:
        parts.append(NULL)
        return
    parts.append(str(node.val))
    _write(node.left, parts)
    _write(node.right, parts)


def _read(tokens, cursor):
    tok = tokens[cursor[0]]
    cursor[0] += 1
    if tok == NULL:
        return None
    node = TreeNode(int(tok))
    node.left = _read(tokens, cursor)
    node.right = _read(tokens, cursor)
    return node


APPROACHES = [
    {"id": "preorder", "label": "Preorder with null markers", "fn": round_trip,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"root": "node", "parts": "queue", "tokens": "array", "rebuilt": "node"}},
]
