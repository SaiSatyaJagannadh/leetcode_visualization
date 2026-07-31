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


def collect_each_group(head, k):
    #> Gather k nodes into a list first, then relink them backwards. The pointer
    #> surgery becomes ordinary indexing, at the cost of holding k nodes — the
    #> in-place version does the same job with three pointers and no storage.
    dummy = ListNode(0)
    dummy.next = head
    tail = dummy
    node = head
    while node is not None:
        block = []
        probe = node
        while probe is not None and len(block) < k:
            block.append(probe)
            probe = probe.next
        if len(block) < k:
            #> A short block is left exactly as it is, so attach it untouched.
            tail.next = node
            break
        #> Relink the block in reverse: each node points at the one before it.
        for i in range(len(block) - 1, 0, -1):
            block[i].next = block[i - 1]
        #> The block's old head is now its tail, and points at whatever follows.
        block[0].next = probe
        tail.next = block[len(block) - 1]
        tail = block[0]
        node = probe
    return dummy.next


APPROACHES = [
    {"id": "collect", "label": "Collect k, relink backwards", "fn": collect_each_group,
     "complexity": {"time": "O(n)", "space": "O(k)"},
     "viz": {"head": "node", "block": "array", "dummy": "node", "tail": "node"}},
    {"id": "groups", "label": "Check ahead, then reverse", "fn": group_by_group,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"head": "node", "dummy": "node", "group_prev": "node", "kth": "node", "node": "node", "prev": "node"}},
]
