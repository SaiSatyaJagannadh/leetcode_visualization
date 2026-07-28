from structs import ListNode, build_list

META = {
    "slug": "add-two-numbers",
    "title": "Add Two Numbers",
    "pattern": "Linked List",
    "difficulty": "Medium",
    "leetcode": 2,
    "prompt": "Two numbers are stored as linked lists with their digits reversed, least significant first. Add them and return the sum in the same form.",
    "examples": [
        {"input": "l1 = [2,4,3], l2 = [5,6,4]", "output": "[7,0,8]", "why": "342 + 465 = 807."},
        {"input": "l1 = [9,9], l2 = [1]", "output": "[0,0,1]", "why": "99 + 1 = 100, and the carry creates a new digit."},
    ],
    "constraints": ["1 <= length of each list <= 100", "Each node holds a single digit"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": lambda: {"a": build_list([2, 4, 3]), "b": build_list([5, 6, 4])}},
    {"id": "edge", "label": "Carry past the end", "input": lambda: {"a": build_list([9, 9]), "b": build_list([1])}},
    {"id": "worst-case", "label": "Different lengths", "input": lambda: {"a": build_list([1]), "b": build_list([9, 9, 9])}},
]


def digit_by_digit(a, b):
    dummy = ListNode(0)
    tail = dummy
    carry = 0
    #> Keep going while either list has digits left, or a carry is still pending.
    while a is not None or b is not None or carry:
        total = carry
        if a is not None:
            total += a.val
            a = a.next
        if b is not None:
            total += b.val
            b = b.next
        #> Reversed storage means we meet the digits in the order we'd add them
        #> by hand, so the carry always flows forward into the next node.
        carry = total // 10
        tail.next = ListNode(total % 10)
        tail = tail.next
    return dummy.next


APPROACHES = [
    {"id": "digits", "label": "Digit by digit", "fn": digit_by_digit,
     "complexity": {"time": "O(max(m,n))", "space": "O(max(m,n))"},
     "viz": {"a": "node", "b": "node", "dummy": "node", "tail": "node"}},
]
