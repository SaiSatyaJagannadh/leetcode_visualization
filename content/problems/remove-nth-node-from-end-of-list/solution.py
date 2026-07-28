from structs import ListNode, build_list

META = {
    "slug": "remove-nth-node-from-end-of-list",
    "title": "Remove Nth Node From End of List",
    "pattern": "Linked List",
    "difficulty": "Medium",
    "leetcode": 19,
    "prompt": "Delete the nth node counting back from the end of the list and return the head. Do it in a single pass.",
    "examples": [
        {"input": "head = [1,2,3,4,5], n = 2", "output": "[1,2,3,5]"},
        {"input": "head = [1], n = 1", "output": "[]"},
    ],
    "constraints": ["1 <= number of nodes <= 30", "1 <= n <= number of nodes"],
}

VARIANTS = [
    {"id": "typical", "label": "From the middle", "input": lambda: {"head": build_list([1, 2, 3, 4, 5]), "n": 2}},
    {"id": "edge", "label": "Remove the head", "input": lambda: {"head": build_list([1, 2]), "n": 2}},
    {"id": "worst-case", "label": "Only node", "input": lambda: {"head": build_list([1]), "n": 1}},
]


def two_pass(head, n):
    #> Count first, then walk to the position — simple, but reads the list twice.
    length = 0
    node = head
    while node is not None:
        length += 1
        node = node.next
    dummy = ListNode(0)
    dummy.next = head
    before = dummy
    for _ in range(length - n):
        before = before.next
    before.next = before.next.next
    return dummy.next


def gap_pointers(head, n):
    dummy = ListNode(0)
    dummy.next = head
    #> Open a gap of exactly n nodes between the two pointers.
    lead = dummy
    for _ in range(n):
        lead = lead.next
    trail = dummy
    #> Now advance both together. When lead hits the end, trail is n from it,
    #> which puts it exactly one before the node we want gone.
    while lead.next is not None:
        lead = lead.next
        trail = trail.next
    trail.next = trail.next.next  #> Unlink by pointing past it.
    #> Returning dummy.next rather than head is what handles deleting the head.
    return dummy.next


APPROACHES = [
    {"id": "two-pass", "label": "Count, then walk", "fn": two_pass,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"head": "node", "node": "node", "before": "node", "dummy": "node"}},
    {"id": "gap", "label": "Two pointers, one pass", "fn": gap_pointers,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"head": "node", "lead": "node", "trail": "node", "dummy": "node"}},
]
