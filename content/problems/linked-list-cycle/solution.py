from structs import build_list

META = {
    "slug": "linked-list-cycle",
    "title": "Linked List Cycle",
    "pattern": "Linked List",
    "difficulty": "Easy",
    "leetcode": 141,
    "prompt": "Decide whether a linked list loops back on itself. Solve it using constant extra space.",
    "examples": [
        {"input": "head = [3,2,0,-4], tail connects to index 1", "output": "true"},
        {"input": "head = [1,2]", "output": "false"},
    ],
    "constraints": ["0 <= number of nodes <= 10^4", "Must use O(1) space"],
}

VARIANTS = [
    {"id": "typical", "label": "Has a cycle", "input": lambda: {"head": build_list([3, 2, 0, -4], cycle_at=1)}},
    {"id": "edge", "label": "No cycle", "input": lambda: {"head": build_list([1, 2, 3])}},
    {"id": "worst-case", "label": "Loops to the head", "input": lambda: {"head": build_list([1, 2, 3, 4], cycle_at=0)}},
]


def seen_set(head):
    #> Remembering every node works, but costs memory proportional to the list.
    seen = {}
    node = head
    while node is not None:
        if node.nid in seen:
            return True
        seen[node.nid] = True
        node = node.next
    return False


def floyd(head):
    #> Two runners at different speeds. On a straight list the fast one falls off
    #> the end; on a loop it laps the slow one, because the gap between them
    #> shrinks by exactly one node per step and can never jump past zero.
    slow = head
    fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next  #> One step.
        fast = fast.next.next  #> Two steps.
        if slow is fast:
            #> They met, which is only possible inside a loop.
            return True
    #> fast ran out of list, so there was nothing to loop around.
    return False


APPROACHES = [
    {"id": "seen", "label": "Remember every node", "fn": seen_set,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"head": "node", "node": "node"}},
    {"id": "floyd", "label": "Fast and slow pointers", "fn": floyd,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"head": "node", "slow": "node", "fast": "node"}},
]
