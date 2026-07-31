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


def find_the_last_non_nine(digits):
    #> Locate rather than propagate. Adding one only ever changes the trailing
    #> run of nines plus the digit in front of it, so find that digit first and
    #> write the answer directly — no carry variable at all.
    out = list(digits)
    at = -1
    for i in range(len(out)):
        if out[i] != 9:
            #> Remember the rightmost digit that can absorb the carry.
            at = i
    if at == -1:
        #> Every digit is a nine, so the number gains a place.
        return [1] + [0] * len(out)
    out[at] += 1
    for i in range(at + 1, len(out)):
        #> Everything after it was a nine and rolls over to zero.
        out[i] = 0
    return out


APPROACHES = [
    {"id": "locate", "label": "Find the last non-nine", "fn": find_the_last_non_nine,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"digits": "array", "out": "array", "at": "pointer:out", "i": "pointer:out"}},
    {"id": "carry", "label": "Carry from the right", "fn": carry_backwards,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"digits": "array", "out": "array", "i": "pointer:out"}},
]
