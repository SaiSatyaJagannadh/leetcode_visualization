"""Pointer redirection, a cycle, and a dummy head — the three awkward cases."""

from structs import ListNode, build_list

META = {"slug": "_linkedlist", "title": "Linked list renderer", "pattern": "Fixture"}

VARIANTS = [
    {"id": "typical", "label": "Five nodes", "input": lambda: {"head": build_list([1, 2, 3, 4, 5])}},
    {"id": "edge", "label": "Single node", "input": lambda: {"head": build_list([7])}},
]


def reverse(head):
    prev = None  #> Nothing is behind us yet, so the new tail points at nothing.
    while head is not None:
        nxt = head.next  #> Save the rest of the list before we cut the link.
        head.next = prev  #> The redirection: this arrow now points backwards.
        prev = head  #> Everything up to here is reversed.
        head = nxt
    return prev


def merge_dummy(head):
    #> A dummy head means we never special-case the first node.
    dummy = ListNode(0)
    tail = dummy
    while head is not None:
        #> Copy every value into a fresh chain hanging off the dummy.
        tail.next = ListNode(head.val * 10)
        tail = tail.next
        head = head.next
    return dummy.next


APPROACHES = [
    {
        "id": "reverse",
        "label": "Reverse in place",
        "fn": reverse,
        "complexity": {"time": "O(n)", "space": "O(1)"},
        "viz": {"head": "node", "prev": "node", "nxt": "node"},
    },
    {
        "id": "dummy",
        "label": "Dummy head",
        "fn": merge_dummy,
        "complexity": {"time": "O(n)", "space": "O(n)"},
        "viz": {"head": "node", "dummy": "node", "tail": "node"},
    },
]
