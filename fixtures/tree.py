"""Unbalanced shape, an insert mid-traversal, and a pruned subtree."""

from structs import TreeNode, build_tree, layout_tree

META = {"slug": "_tree", "title": "Tree renderer", "pattern": "Fixture"}

VARIANTS = [
    {
        "id": "typical",
        "label": "Unbalanced",
        "input": lambda: {"root": build_tree([8, 3, 10, 1, 6, None, 14, None, None, 4, 7])},
    },
    {"id": "edge", "label": "Right spine", "input": lambda: {"root": build_tree([1, None, 2, None, 3, None, 4])}},
]


def inorder(root):
    out = []
    stack = []
    node = root
    while node is not None or stack:
        while node is not None:
            #> Dive left as far as the tree allows, remembering the way back.
            stack.append(node)
            node = node.left
        node = stack.pop()  #> Nothing further left, so this node is next in order.
        out.append(node.val)
        node = node.right  #> Its left subtree is done; cross to the right.
    return out


def bst_insert(root):
    #> Walk down as if searching for 5, then hang it off the node we fall out of.
    node = root
    while True:
        if 5 < node.val:
            if node.left is None:
                node.left = TreeNode(5)
                break
            node = node.left  #> 5 is smaller, so the whole right subtree is pruned.
        else:
            if node.right is None:
                node.right = TreeNode(5)
                break
            node = node.right  #> 5 is larger, so the whole left subtree is pruned.
    layout_tree(root)
    return root.val


APPROACHES = [
    {
        "id": "inorder",
        "label": "Iterative in-order",
        "fn": inorder,
        "complexity": {"time": "O(n)", "space": "O(h)"},
        "viz": {"root": "node", "node": "node", "stack": "stack"},
    },
    {
        "id": "insert",
        "label": "BST insert",
        "fn": bst_insert,
        "complexity": {"time": "O(h)", "space": "O(1)"},
        "viz": {"root": "node", "node": "node"},
    },
]
