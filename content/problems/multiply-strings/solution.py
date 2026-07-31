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


def via_integers(a, b):
    #> Read both strings into whole numbers, multiply, print. One line of real
    #> work — but it leans entirely on Python integers being unbounded. In a
    #> language where they are not, the digits overflow long before the answer
    #> is reached, and the positional method above is the only option left.
    x = 0
    for ch in a:
        #> Shift left one place and drop the new digit in.
        x = x * 10 + int(ch)
    y = 0
    for ch in b:
        y = y * 10 + int(ch)
    product = x * y
    if product == 0:
        return "0"
    out = []
    while product > 0:
        #> Peel digits off the right, so they come out reversed.
        out.append(str(product % 10))
        product = product // 10
    return "".join(out[::-1])


APPROACHES = [
    {"id": "via-integers", "label": "Convert, multiply, print", "fn": via_integers,
     "complexity": {"time": "O(m + n)", "space": "O(m + n)"},
     "viz": {"out": "array"}},
    {"id": "long", "label": "Long multiplication", "fn": long_multiplication,
     "complexity": {"time": "O(mn)", "space": "O(m + n)"},
     "viz": {"digits": "array", "i": "pointer:a", "j": "pointer:b"}},
]
