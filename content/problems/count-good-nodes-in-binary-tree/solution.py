from structs import build_tree

META = {
    "slug": "count-good-nodes-in-binary-tree",
    "title": "Count Good Nodes in Binary Tree",
    "pattern": "Trees",
    "difficulty": "Medium",
    "leetcode": 1448,
    "prompt": "A node is good when nothing on the path from the root down to it is larger than it. Count the good nodes.",
    "examples": [
        {"input": "root = [3,1,4,3,null,1,5]", "output": "4"},
        {"input": "root = [3,3,null,4,2]", "output": "3"},
    ],
    "constraints": ["1 <= number of nodes <= 10^5"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": lambda: {"root": build_tree([3, 1, 4, 3, None, 1, 5])}},
    {"id": "edge", "label": "Root only is good", "input": lambda: {"root": build_tree([5, 4, 3])}},
    {"id": "worst-case", "label": "Every node good", "input": lambda: {"root": build_tree([1, 2, 3, 4])}},
]


def carry_the_max(root):
    #> Carrying the largest value seen so far *down* the path is the trick: a node
    #> only needs one number to decide, not a list of everything above it.
    return _walk(root, root.val)


def _walk(node, best):
    if node is None:
        return 0
    #> Good means nothing above it beat it. Equal still counts as good.
    count = 1 if node.val >= best else 0
    #> Both children inherit the larger of the running max and this node.
    higher = max(best, node.val)
    count += _walk(node.left, higher)
    count += _walk(node.right, higher)
    return count


APPROACHES = [
    {"id": "carry-max", "label": "Carry the path maximum down", "fn": carry_the_max,
     "complexity": {"time": "O(n)", "space": "O(h)"},
     "viz": {"root": "node", "$calls": "recursion"}},
]
