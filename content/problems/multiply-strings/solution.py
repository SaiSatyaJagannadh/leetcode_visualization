META = {
    "slug": "multiply-strings",
    "title": "Multiply Strings",
    "pattern": "Math & Geometry",
    "difficulty": "Medium",
    "leetcode": 43,
    "prompt": "Multiply two non-negative integers given as strings, without converting them to numbers directly.",
    "examples": [
        {"input": 'num1 = "12", num2 = "34"', "output": '"408"'},
        {"input": 'num1 = "0", num2 = "999"', "output": '"0"'},
    ],
    "constraints": ["1 <= len(num1), len(num2) <= 200", "No leading zeros"],
}

VARIANTS = [
    {"id": "typical", "label": "Two digits each", "input": {"a": "12", "b": "34"}},
    {"id": "edge", "label": "Times zero", "input": {"a": "0", "b": "999"}},
    {"id": "worst-case", "label": "Heavy carrying", "input": {"a": "99", "b": "99"}},
]


def long_multiplication(a, b):
    if a == "0" or b == "0":
        return "0"
    #> Digit i of a times digit j of b always lands at position i + j, with any
    #> carry going to i + j + 1. That fixed mapping is the whole algorithm.
    digits = [0] * (len(a) + len(b))
    for i in range(len(a) - 1, -1, -1):
        for j in range(len(b) - 1, -1, -1):
            product = int(a[i]) * int(b[j])
            pos = i + j + 1
            total = digits[pos] + product
            digits[pos] = total % 10
            #> Carry accumulates into the slot above; it is resolved when that
            #> slot is itself processed, so no separate carry pass is needed.
            digits[pos - 1] += total // 10
    #> Drop the leading zero the extra slot may have left behind.
    start = 0
    while start < len(digits) - 1 and digits[start] == 0:
        start += 1
    return "".join(str(d) for d in digits[start:])


APPROACHES = [
    {"id": "long", "label": "Long multiplication", "fn": long_multiplication,
     "complexity": {"time": "O(mn)", "space": "O(m + n)"},
     "viz": {"digits": "array", "i": "pointer:a", "j": "pointer:b"}},
]
