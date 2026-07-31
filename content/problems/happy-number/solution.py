META = {
    "slug": "happy-number",
    "title": "Happy Number",
    "pattern": "Math & Geometry",
    "difficulty": "Easy",
    "leetcode": 202,
    "prompt": "Repeatedly replace a number by the sum of the squares of its digits. It is happy if this reaches 1, and unhappy if it falls into a loop that never does.",
    "examples": [
        {"input": "n = 19", "output": "true", "why": "19 → 82 → 68 → 100 → 1."},
        {"input": "n = 2", "output": "false", "why": "It enters a cycle."},
    ],
    "constraints": ["1 <= n <= 2^31 - 1"],
}

VARIANTS = [
    {"id": "typical", "label": "Happy", "input": {"n": 19}},
    {"id": "edge", "label": "Already one", "input": {"n": 1}},
    {"id": "worst-case", "label": "Cycles forever", "input": {"n": 2}},
]


def seen_set(n):
    #> The sequence either reaches 1 or repeats a value. Remembering what we've
    #> seen turns "loops forever" into a condition we can actually detect.
    seen = {}
    value = n
    while value != 1:
        if value in seen:
            #> Back somewhere we've been, so this loops without ever reaching 1.
            return False
        seen[value] = True
        total = 0
        x = value
        while x > 0:
            digit = x % 10
            total += digit * digit
            x = x // 10
        value = total
    return True


def floyd_cycle(n):
    #> The sequence is a linked list in disguise: each value points at exactly
    #> one successor. So the tortoise-and-hare trick works, and it needs no
    #> memory at all — the set version's whole cost disappears.
    slow = n
    fast = _square_digits(n)
    while fast != 1 and slow != fast:
        #> One step for slow, two for fast. If there is a loop the fast pointer
        #> laps the slow one; if there is not, fast reaches 1 first.
        slow = _square_digits(slow)
        fast = _square_digits(_square_digits(fast))
    return fast == 1


def _square_digits(x):
    total = 0
    while x > 0:
        digit = x % 10
        total += digit * digit
        x = x // 10
    return total


APPROACHES = [
    {"id": "floyd", "label": "Tortoise and hare", "fn": floyd_cycle,
     "complexity": {"time": "O(log n)", "space": "O(1)"},
     "viz": {"$calls": "recursion"}},
    {"id": "seen", "label": "Detect the repeat", "fn": seen_set,
     "complexity": {"time": "O(log n)", "space": "O(log n)"},
     "viz": {"seen": "map"}},
]
