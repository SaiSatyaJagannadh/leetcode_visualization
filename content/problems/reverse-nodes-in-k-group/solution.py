from structs import ListNode, build_list

META = {
    "slug": "reverse-nodes-in-k-group",
    "title": "Reverse Nodes in K-Group",
    "pattern": "Linked List",
    "difficulty": "Hard",
    "leetcode": 25,
    "prompt": "Reverse the list in blocks of k nodes. A trailing block shorter than k stays in its original order.",
    "examples": [
        {"input": "head = [1,2,3,4,5], k = 2", "output": "[2,1,4,3,5]"},
        {"input": "head = [1,2,3,4,5], k = 3", "output": "[3,2,1,4,5]"},
    ],
    "constraints": ["1 <= k <= number of nodes <= 5000"],
}

VARIANTS = [
    {"id": "typical", "label": "k = 2", "input": lambda: {"head": build_list([1, 2, 3, 4, 5]), "k": 2}},
    {"id": "edge", "label": "k = 1", "input": lambda: {"head": build_list([1, 2, 3]), "k": 1}},
    {"id": "worst-case", "label": "k = 3, remainder left", "input": lambda: {"head": build_list([1, 2, 3, 4, 5]), "k": 3}},
]


def group_by_group(head, k):
    dummy = ListNode(0)
    dummy.next = head
    #> group_prev is the node just before the block we're about to reverse.
    group_prev = dummy
    while True:
        #> Look ahead k nodes first. If the block is short, the problem says to
        #> leave it alone, so checking before touching anything avoids undoing work.
        kth = group_prev
        for _ in range(k):
            kth = kth.next
            if kth is None:
                return dummy.next
        group_next = kth.next

        #> Reverse the block, seeding prev with what follows it so the block's
        #> old head ends up pointing at the rest of the list automatically.
        prev = group_next
        node = group_prev.next
        while node is not group_next:
            nxt = node.next
            node.next = prev
            prev = node
            node = nxt

        #> group_prev.next is still the block's old head, which is now its tail.
        new_prev = group_prev.next
        group_prev.next = kth  #> kth was the block's last node, now its first.
        group_prev = new_prev


APPROACHES = [
    {"id": "groups", "label": "Check ahead, then reverse", "fn": group_by_group,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"head": "node", "dummy": "node", "group_prev": "node", "kth": "node", "node": "node", "prev": "node"}},
]
