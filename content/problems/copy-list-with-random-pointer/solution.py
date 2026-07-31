from structs import ListNode, build_list

META = {
    "slug": "copy-list-with-random-pointer",
    "title": "Copy List With Random Pointer",
    "pattern": "Linked List",
    "difficulty": "Medium",
    "leetcode": 138,
    "prompt": "Each node has a next pointer and a random pointer that may target any node or nothing. Make a deep copy in which every pointer targets the copies, never the originals.",
    "examples": [
        {"input": "head = [[7,null],[13,0],[11,4],[10,2],[1,0]]", "output": "an identical, independent list"},
        {"input": "head = []", "output": "[]"},
    ],
    "constraints": ["0 <= number of nodes <= 1000"],
}


def make(vals, randoms):
    head = build_list(vals)
    nodes = []
    n = head
    while n is not None:
        nodes.append(n)
        n = n.next
    for i, target in enumerate(randoms):
        if target is not None:
            nodes[i].random = nodes[target]
    return {"head": head}


VARIANTS = [
    {"id": "typical", "label": "Random links", "input": lambda: make([7, 13, 11, 10], [None, 0, 3, 2])},
    {"id": "edge", "label": "Single node", "input": lambda: make([1], [0])},
    {"id": "worst-case", "label": "All point to the head", "input": lambda: make([1, 2, 3], [0, 0, 0])},
]


def two_pass_map(head):
    if head is None:
        return None
    #> First pass: create every copy and record which original it belongs to.
    #> The map is what lets a random pointer be translated later — at the time we
    #> meet it, its target may not have been copied yet.
    copies = {}
    node = head
    while node is not None:
        copies[node.nid] = ListNode(node.val)
        node = node.next
    #> Second pass: now that every copy exists, wire both pointers through the map.
    node = head
    while node is not None:
        clone = copies[node.nid]
        clone.next = copies[node.next.nid] if node.next is not None else None
        clone.random = copies[node.random.nid] if node.random is not None else None
        node = node.next
    return copies[head.nid]


def interleave(head):
    if head is None:
        return None
    #> No map at all. Weave each copy in directly behind its original, so the
    #> original itself becomes the lookup table: orig.next IS orig's copy.
    node = head
    while node is not None:
        made = ListNode(node.val)
        made.next = node.next
        node.next = made
        node = made.next
    #> Now a random pointer translates in one hop: the copy of node.random is
    #> sitting immediately after it.
    node = head
    while node is not None:
        if node.random is not None:
            node.next.random = node.random.next
        node = node.next.next
    #> Finally unpick the two lists, restoring the original as we go.
    node = head
    out = head.next
    while node is not None:
        made = node.next
        node.next = made.next
        if made.next is not None:
            made.next = made.next.next
        node = node.next
    return out


APPROACHES = [
    {"id": "interleave", "label": "Weave the copies in", "fn": interleave,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"head": "node", "node": "node", "made": "node", "out": "node"}},
    {"id": "map", "label": "Copy first, wire second", "fn": two_pass_map,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"head": "node", "node": "node", "clone": "node"}},
]
