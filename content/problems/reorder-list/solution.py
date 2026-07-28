from structs import build_list

META = {
    "slug": "reorder-list",
    "title": "Reorder List",
    "pattern": "Linked List",
    "difficulty": "Medium",
    "leetcode": 143,
    "prompt": "Rearrange a list so it reads first node, last node, second node, second-to-last, and so on. Rewire the nodes rather than copying their values.",
    "examples": [
        {"input": "head = [1,2,3,4]", "output": "[1,4,2,3]"},
        {"input": "head = [1,2,3,4,5]", "output": "[1,5,2,4,3]"},
    ],
    "constraints": ["1 <= number of nodes <= 5 * 10^4"],
}

VARIANTS = [
    {"id": "typical", "label": "Even length", "input": lambda: {"head": build_list([1, 2, 3, 4])}},
    {"id": "edge", "label": "Two nodes", "input": lambda: {"head": build_list([1, 2])}},
    {"id": "worst-case", "label": "Odd length", "input": lambda: {"head": build_list([1, 2, 3, 4, 5])}},
]


def split_reverse_weave(head):
    #> Step one: find the middle with fast and slow runners.
    slow = head
    fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next

    #> Step two: reverse everything after the middle, so the back half now runs
    #> backwards and its head is the list's old tail.
    second = slow.next
    slow.next = None
    prev = None
    while second is not None:
        nxt = second.next
        second.next = prev
        prev = second
        second = nxt

    #> Step three: weave. Both halves now start at the ends we want to alternate.
    first = head
    second = prev
    while second is not None:
        first_next = first.next
        second_next = second.next
        first.next = second  #> Front node points at a back node.
        second.next = first_next  #> Which points at the next front node.
        first = first_next
        second = second_next
    return head


APPROACHES = [
    {"id": "split-reverse-weave", "label": "Split, reverse, weave", "fn": split_reverse_weave,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"head": "node", "slow": "node", "fast": "node", "first": "node", "second": "node", "prev": "node"}},
]
