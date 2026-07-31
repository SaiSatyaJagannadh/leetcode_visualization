from structs import TreeNode, build_tree, layout_tree

META = {
    "slug": "serialize-and-deserialize-binary-tree",
    "title": "Serialize and Deserialize Binary Tree",
    "pattern": "Trees",
    "difficulty": "Hard",
    "leetcode": 297,
    "prompt": "Turn a binary tree into a string, and turn that string back into the identical tree. The trace does both and checks the round trip.",
    "examples": [
        {"input": "root = [1,2,3,null,null,4,5]", "output": "[1,2,3,null,null,4,5]",
         "why": "The tree survives the round trip. Which encoding was used in between is an implementation detail, and the two approaches here choose differently."},
        {"input": "root = []", "output": "[]"},
        {"input": "root = [1,null,2]", "output": "[1,null,2]",
         "why": "A missing child must be recorded, or this would come back as [1,2] with the child on the wrong side."},
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
    #> Return the rebuilt tree, not the string. The encoding is a private
    #> choice; what the problem actually promises is that the tree survives.
    return _levels(rebuilt)


def _levels(root):
    #> Level order with explicit nulls, the same shape the examples use.
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


def level_order_round_trip(root):
    #> Breadth-first instead of preorder. Markers still make it unambiguous, but
    #> now they hold absent slots within a level, so the string reads like the
    #> array form the examples use. A completely different encoding that has to
    #> rebuild exactly the same tree.
    parts = []
    queue = [root]
    while queue:
        node = queue.pop(0)
        if node is None:
            parts.append(NULL)
            continue
        parts.append(str(node.val))
        #> Both children are enqueued even when absent; the marker holds the slot.
        queue.append(node.left)
        queue.append(node.right)
    text = ",".join(parts)

    tokens = text.split(",")
    if tokens[0] == NULL:
        return []
    rebuilt = TreeNode(int(tokens[0]))
    #> No cursor and no recursion: the queue itself remembers which parent is
    #> still waiting for children, which is the job preorder gave the call stack.
    waiting = [rebuilt]
    i = 1
    while waiting and i < len(tokens):
        node = waiting.pop(0)
        if tokens[i] != NULL:
            node.left = TreeNode(int(tokens[i]))
            waiting.append(node.left)
        i += 1
        if i < len(tokens) and tokens[i] != NULL:
            node.right = TreeNode(int(tokens[i]))
            waiting.append(node.right)
        i += 1
    layout_tree(rebuilt)
    return _levels(rebuilt)


APPROACHES = [
    {"id": "level-order", "label": "Level order with markers", "fn": level_order_round_trip,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"root": "node", "queue": "queue", "parts": "queue", "waiting": "queue"}},
    {"id": "preorder", "label": "Preorder with null markers", "fn": round_trip,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"root": "node", "parts": "queue", "tokens": "array", "rebuilt": "node"}},
]
