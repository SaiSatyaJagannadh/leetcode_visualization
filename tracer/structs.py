"""Node types every solution shares, so the tracer can serialise them.

Layout is assigned here, at construction, because this is the only place that
sees the whole shape at once. Coordinates are abstract units; the renderer fits
them to its viewBox. A node keeps its position for the whole run, so pointer
redirection animates as arrows moving, not boxes shuffling.
"""

from itertools import count

_ids = count()
_next_id = _ids.__next__  # `next` is a parameter name below, so bind it here


class ListNode:
    __slots__ = ("val", "next", "nid", "pos")

    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
        self.nid = _next_id()
        self.pos = None


class TreeNode:
    __slots__ = ("val", "left", "right", "nid", "pos")

    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
        self.nid = _next_id()
        self.pos = None


NODE_TYPES = (ListNode, TreeNode)


def build_list(vals, cycle_at=None):
    """Linked list laid out left to right. cycle_at points the tail back to an index."""
    head = tail = None
    nodes = []
    for i, v in enumerate(vals):
        n = ListNode(v)
        n.pos = (float(i), 0.0)
        nodes.append(n)
        if head is None:
            head = tail = n
        else:
            tail.next = n
            tail = n
    if cycle_at is not None and nodes:
        tail.next = nodes[cycle_at]
    return head


def build_tree(vals):
    """LeetCode level-order list, None for a missing child. Laid out in-order."""
    if not vals or vals[0] is None:
        return None
    root = TreeNode(vals[0])
    queue = [root]
    i = 1
    while queue and i < len(vals):
        node = queue.pop(0)
        for side in ("left", "right"):
            if i >= len(vals):
                break
            v = vals[i]
            i += 1
            if v is None:
                continue
            child = TreeNode(v)
            setattr(node, side, child)
            queue.append(child)
    layout_tree(root)
    return root


def layout_tree(root):
    """x = in-order slot, y = depth. Never overlaps, needs no force simulation."""
    slot = count()

    def walk(node, depth):
        if node is None:
            return
        walk(node.left, depth + 1)
        # ponytail: in-order slot is assigned once. A node inserted mid-run lands
        # between its neighbours (see _place); re-layout only if that reads badly.
        node.pos = (float(next(slot)), float(depth))
        walk(node.right, depth + 1)

    walk(root, 0)
