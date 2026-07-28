META = {
    "slug": "number-of-1-bits",
    "title": "Number of 1 Bits",
    "pattern": "Bit Manipulation",
    "difficulty": "Easy",
    "leetcode": 191,
    "prompt": "Count the 1 bits in the binary form of an unsigned integer.",
    "examples": [
        {"input": "n = 11", "output": "3", "why": "1011 in binary."},
        {"input": "n = 128", "output": "1", "why": "10000000."},
    ],
    "constraints": ["0 <= n < 2^32"],
}

VARIANTS = [
    {"id": "typical", "label": "n = 11", "input": {"n": 11}},
    {"id": "edge", "label": "n = 0", "input": {"n": 0}},
    {"id": "worst-case", "label": "Sparse bits", "input": {"n": 128}},
]


def shift_every_bit(n):
    #> Walk every bit position, whether it holds a 1 or not.
    count = 0
    x = n
    while x > 0:
        count += x & 1
        x = x >> 1
    return count


def clear_lowest_set(n):
    #> Subtracting one flips the lowest 1 to 0 and everything below it to 1, so
    #> AND-ing with the original clears exactly that bit. The loop therefore runs
    #> once per 1 bit, not once per position — much better on sparse numbers.
    count = 0
    x = n
    while x > 0:
        x = x & (x - 1)
        count += 1
    return count


APPROACHES = [
    {"id": "shift", "label": "Shift through every bit", "fn": shift_every_bit,
     "complexity": {"time": "O(32)", "space": "O(1)"},
     "viz": {}},
    {"id": "clear", "label": "Clear the lowest set bit", "fn": clear_lowest_set,
     "complexity": {"time": "O(set bits)", "space": "O(1)"},
     "viz": {}},
]
