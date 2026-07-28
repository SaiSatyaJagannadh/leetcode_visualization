from structs import build_list

META = {
    "slug": "reverse-linked-list",
    "title": "Reverse Linked List",
    "pattern": "Linked List",
    "difficulty": "Easy",
    "leetcode": 206,
    "prompt": (
        "Given the head of a singly linked list, turn every arrow around so the "
        "last node becomes the first, and return the new head."
    ),
    "examples": [
        {"input": "head = [1,2,3,4,5]", "output": "[5,4,3,2,1]"},
        {"input": "head = []", "output": "[]", "why": "An empty list is already reversed."},
    ],
    "constraints": ["0 <= number of nodes <= 5000", "-5000 <= node value <= 5000"],
}

VARIANTS = [
    {"id": "typical", "label": "Five nodes", "input": lambda: {"head": build_list([1, 2, 3, 4, 5])}},
    {"id": "edge", "label": "Single node", "input": lambda: {"head": build_list([1])}},
    {"id": "worst-case", "label": "Two nodes", "input": lambda: {"head": build_list([1, 2])}},
]


def iterative(head):
    #> prev is the part already reversed. It starts empty, which is the new tail.
    prev = None
    node = head
    while node is not None:
        #> Grab the rest of the list first — the next line destroys this link.
        nxt = node.next
        node.next = prev  #> The reversal itself: one arrow, turned around.
        prev = node  #> The reversed part just grew by one node.
        node = nxt  #> Step into what's left of the original list.
    #> node fell off the end, so prev is sitting on the old last node.
    return prev


def recursive(head):
    if head is None or head.next is None:
        #> An empty list, or a single node, is its own reversal.
        return head
    #> Trust the recursion to reverse everything after this node, then fix one link.
    rest = recursive(head.next)
    head.next.next = head  #> The node behind us now points back at us.
    head.next = None  #> And we become the tail until our caller fixes it.
    return rest


APPROACHES = [
    {
        "id": "iterative",
        "label": "Iterative",
        "fn": iterative,
        "complexity": {"time": "O(n)", "space": "O(1)"},
        "viz": {"head": "node", "prev": "node", "node": "node", "nxt": "node"},
    },
    {
        "id": "recursive",
        "label": "Recursive",
        "fn": recursive,
        "complexity": {"time": "O(n)", "space": "O(n)"},
        "viz": {"head": "node", "rest": "node", "$calls": "recursion"},
    },
]
