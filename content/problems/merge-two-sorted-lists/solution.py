from structs import ListNode, build_list

META = {
    "slug": "merge-two-sorted-lists",
    "title": "Merge Two Sorted Lists",
    "pattern": "Linked List",
    "difficulty": "Easy",
    "leetcode": 21,
    "prompt": "Two sorted linked lists are given. Splice their nodes together into one sorted list and return its head.",
    "examples": [
        {"input": "list1 = [1,2,4], list2 = [1,3,4]", "output": "[1,1,2,3,4,4]"},
        {"input": "list1 = [], list2 = [0]", "output": "[0]"},
    ],
    "constraints": ["0 <= length of each list <= 50", "Both lists are sorted ascending"],
}

VARIANTS = [
    {"id": "typical", "label": "Interleaving", "input": lambda: {"a": build_list([1, 2, 4]), "b": build_list([1, 3, 4])}},
    {"id": "edge", "label": "One empty", "input": lambda: {"a": None, "b": build_list([0])}},
    {"id": "worst-case", "label": "No overlap", "input": lambda: {"a": build_list([1, 2]), "b": build_list([8, 9])}},
]


def with_dummy(a, b):
    #> A throwaway head means the first real node needs no special case — we can
    #> always just write to tail.next.
    dummy = ListNode(0)
    tail = dummy
    while a is not None and b is not None:
        #> Take the smaller head; ties can go either way without breaking order.
        if a.val <= b.val:
            tail.next = a
            a = a.next
        else:
            tail.next = b
            b = b.next
        tail = tail.next
    #> One list is empty now, and the other is already sorted, so attach it whole.
    tail.next = a if a is not None else b
    return dummy.next


APPROACHES = [
    {"id": "dummy", "label": "Dummy head", "fn": with_dummy,
     "complexity": {"time": "O(m + n)", "space": "O(1)"},
     "viz": {"a": "node", "b": "node", "dummy": "node", "tail": "node"}},
]
