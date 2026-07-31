from structs import ListNode, build_list

META = {
    "slug": "merge-k-sorted-lists",
    "title": "Merge K Sorted Lists",
    "pattern": "Linked List",
    "difficulty": "Hard",
    "leetcode": 23,
    "prompt": "Merge k sorted linked lists into one sorted list and return its head.",
    "examples": [
        {"input": "lists = [[1,4,5],[1,3,4],[2,6]]", "output": "[1,1,2,3,4,4,5,6]"},
        {"input": "lists = []", "output": "[]"},
    ],
    "constraints": ["0 <= k <= 10^4", "Each list is sorted ascending"],
}

VARIANTS = [
    {"id": "typical", "label": "Three lists",
     "input": lambda: {"lists": [build_list([1, 4, 5]), build_list([1, 3]), build_list([2, 6])]}},
    {"id": "edge", "label": "One list", "input": lambda: {"lists": [build_list([1, 2])]}},
    {"id": "worst-case", "label": "No overlap",
     "input": lambda: {"lists": [build_list([1, 2]), build_list([8, 9])]}},
]


def pairwise(lists):
    if not lists:
        return None
    #> Merge in pairs, halving the number of lists each round. Merging them one
    #> at a time into an accumulator would re-walk the growing result k times;
    #> pairing means each node is touched only log k times.
    queue = list(lists)
    while len(queue) > 1:
        nxt = []
        for i in range(0, len(queue), 2):
            if i + 1 < len(queue):
                nxt.append(_merge(queue[i], queue[i + 1]))
            else:
                #> Odd one out rides through to the next round untouched.
                nxt.append(queue[i])
        queue = nxt
    return queue[0]


def _merge(a, b):
    dummy = ListNode(0)
    tail = dummy
    while a is not None and b is not None:
        if a.val <= b.val:
            tail.next = a
            a = a.next
        else:
            tail.next = b
            b = b.next
        tail = tail.next
    tail.next = a if a is not None else b
    return dummy.next


def one_at_a_time(lists):
    #> Fold the lists into an accumulator, left to right. Correct, and the reason
    #> pairing exists: the accumulator grows every round, so early nodes get
    #> re-walked once per remaining list instead of once per halving.
    if not lists:
        return None
    out = lists[0]
    for i in range(1, len(lists)):
        #> Each merge walks the whole accumulated result again.
        out = _merge(out, lists[i])
    return out


APPROACHES = [
    {"id": "sequential", "label": "Fold one list at a time", "fn": one_at_a_time,
     "complexity": {"time": "O(k\u00b7n)", "space": "O(1)"},
     "viz": {"lists": "array", "out": "node"}},
    {"id": "pairwise", "label": "Merge in pairs", "fn": pairwise,
     "complexity": {"time": "O(N log k)", "space": "O(1)"},
     "viz": {"queue": "array", "nxt": "array"}},
]
