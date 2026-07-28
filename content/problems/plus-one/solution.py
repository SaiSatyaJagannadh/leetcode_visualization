META = {
    "slug": "plus-one",
    "title": "Plus One",
    "pattern": "Math & Geometry",
    "difficulty": "Easy",
    "leetcode": 66,
    "prompt": "A number is stored as an array of digits, most significant first. Add one to it and return the digits.",
    "examples": [
        {"input": "digits = [1,2,3]", "output": "[1,2,4]"},
        {"input": "digits = [9,9]", "output": "[1,0,0]", "why": "The carry runs off the front and adds a digit."},
    ],
    "constraints": ["1 <= len(digits) <= 100", "No leading zeros"],
}

VARIANTS = [
    {"id": "typical", "label": "No carry", "input": lambda: {"digits": [1, 2, 3]}},
    {"id": "edge", "label": "All nines", "input": lambda: {"digits": [9, 9]}},
    {"id": "worst-case", "label": "Carry stops midway", "input": lambda: {"digits": [1, 9, 9]}},
]


def carry_backwards(digits):
    out = list(digits)
    #> Work right to left, the way addition carries.
    for i in range(len(out) - 1, -1, -1):
        if out[i] < 9:
            #> No carry out of this digit, so nothing further left can change.
            out[i] += 1
            return out
        #> A 9 becomes 0 and passes the carry along.
        out[i] = 0
    #> Falling out of the loop means every digit was a 9, so the number grew by
    #> one place — the only case where the answer is longer than the input.
    return [1] + out


APPROACHES = [
    {"id": "carry", "label": "Carry from the right", "fn": carry_backwards,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"digits": "array", "out": "array", "i": "pointer:out"}},
]
