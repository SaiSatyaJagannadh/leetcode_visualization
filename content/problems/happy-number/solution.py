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


APPROACHES = [
    {"id": "seen", "label": "Detect the repeat", "fn": seen_set,
     "complexity": {"time": "O(log n)", "space": "O(log n)"},
     "viz": {"seen": "map"}},
]
