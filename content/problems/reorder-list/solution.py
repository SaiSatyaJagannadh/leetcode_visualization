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


def index_the_nodes(head):
    #> Collect every node into a list first, then rewire by index: front, back,
    #> front+1, back-1, and so on. No middle to find and nothing to reverse —
    #> the array gives random access the list itself never had, at the cost of
    #> O(n) extra space, which is the whole trade.
    if head is None:
        return None
    nodes = []
    node = head
    while node is not None:
        nodes.append(node)
        node = node.next
    lo = 0
    hi = len(nodes) - 1
    while lo < hi:
        #> Front node points at the back one.
        nodes[lo].next = nodes[hi]
        lo += 1
        if lo == hi:
            #> Odd length: the middle node is now the tail.
            break
        #> And that back node points at the next front one.
        nodes[hi].next = nodes[lo]
        hi -= 1
    #> Whichever node ended in the middle terminates the list.
    nodes[lo].next = None
    return head


APPROACHES = [
    {"id": "index", "label": "Collect and rewire by index", "fn": index_the_nodes,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"head": "node", "nodes": "array", "lo": "pointer:nodes", "hi": "pointer:nodes"}},
    {"id": "split-reverse-weave", "label": "Split, reverse, weave", "fn": split_reverse_weave,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"head": "node", "slow": "node", "fast": "node", "first": "node", "second": "node", "prev": "node"}},
]
