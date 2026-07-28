META = {
    "slug": "counting-bits",
    "title": "Counting Bits",
    "pattern": "Bit Manipulation",
    "difficulty": "Easy",
    "leetcode": 338,
    "prompt": (
        "For every number from 0 to n, count how many 1 bits its binary form "
        "holds. Return the counts as a list."
    ),
    "examples": [
        {"input": "n = 5", "output": "[0,1,1,2,1,2]",
         "why": "0, 1, 10, 11, 100, 101 — the 1s in each."},
        {"input": "n = 0", "output": "[0]"},
    ],
    "constraints": ["0 <= n <= 10^5"],
}

VARIANTS = [
    {"id": "typical", "label": "n = 8", "input": {"n": 8}},
    {"id": "edge", "label": "n = 0", "input": {"n": 0}},
    {"id": "worst-case", "label": "n = 15", "input": {"n": 15}},
]


def shift_each(n):
    out = []
    for v in range(n + 1):
        bits = []
        x = v
        while x > 0:
            bits.append(x & 1)  #> Read the lowest bit, then drop it.
            x = x >> 1
        out.append(sum(bits))
    return out


def dp_from_half(n):
    out = [0] * (n + 1)
    for v in range(1, n + 1):
        #> Halving a number in binary is just dropping its last bit. So v has the
        #> same 1s as v >> 1, plus one more if the bit we dropped was a 1.
        out[v] = out[v >> 1] + (v & 1)
    return out


APPROACHES = [
    {
        "id": "shift",
        "label": "Shift every number",
        "fn": shift_each,
        "complexity": {"time": "O(n log n)", "space": "O(1)"},
        "viz": {"bits": "bits", "out": "array", "v": "pointer:out"},
    },
    {
        "id": "dp",
        "label": "Reuse the half",
        "fn": dp_from_half,
        "complexity": {"time": "O(n)", "space": "O(1)"},
        "viz": {"out": "array", "v": "pointer:out"},
    },
]
