META = {
    "slug": "sum-of-two-integers",
    "title": "Sum of Two Integers",
    "pattern": "Bit Manipulation",
    "difficulty": "Medium",
    "leetcode": 371,
    "prompt": "Add two integers without using the plus or minus operators.",
    "examples": [
        {"input": "a = 1, b = 2", "output": "3"},
        {"input": "a = 2, b = 3", "output": "5"},
    ],
    "constraints": ["-1000 <= a, b <= 1000"],
}

VARIANTS = [
    {"id": "typical", "label": "No carry", "input": {"a": 1, "b": 2}},
    {"id": "edge", "label": "Zero", "input": {"a": 0, "b": 5}},
    {"id": "worst-case", "label": "Carry chain", "input": {"a": 7, "b": 9}},
]


def xor_and_carry(a, b):
    #> XOR is addition that forgets to carry, and AND finds exactly the columns
    #> where a carry was owed. Shifting that left by one puts it where it belongs.
    x = a
    y = b
    while y != 0:
        carry = (x & y) << 1
        x = x ^ y  #> The sum, ignoring carries.
        y = carry  #> Now add the carries in, which may produce more carries.
    return x


APPROACHES = [
    {"id": "xor-carry", "label": "XOR for the sum, AND for the carry", "fn": xor_and_carry,
     "complexity": {"time": "O(32)", "space": "O(1)"},
     "viz": {}},
]
