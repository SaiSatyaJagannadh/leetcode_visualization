META = {
    "slug": "reverse-bits",
    "title": "Reverse Bits",
    "pattern": "Bit Manipulation",
    "difficulty": "Easy",
    "leetcode": 190,
    "prompt": "Reverse the order of the 32 bits of an unsigned integer and return the result.",
    "examples": [
        {"input": "n = 43261596", "output": "964176192"},
        {"input": "n = 1", "output": "2147483648", "why": "The lowest bit becomes the highest."},
    ],
    "constraints": ["The input is exactly 32 bits"],
}

VARIANTS = [
    {"id": "typical", "label": "n = 43261596", "input": {"n": 43261596}},
    {"id": "edge", "label": "n = 1", "input": {"n": 1}},
    {"id": "worst-case", "label": "n = 0", "input": {"n": 0}},
]

WIDTH = 32


def shift_across(n):
    result = 0
    x = n
    for i in range(WIDTH):
        #> Take the lowest bit of the input and push it into the *highest* unused
        #> slot of the output. Shifting the result left each round is what turns
        #> "read forwards" into "write backwards".
        result = (result << 1) | (x & 1)
        x = x >> 1
    return result


def collect_then_rebuild(n):
    #> Read the bits into a list, reverse it, read it back. The shifting version
    #> does the same job with no storage at all — the output register IS the
    #> reversed list, built one bit at a time.
    bits = []
    x = n
    for i in range(WIDTH):
        #> Peel the lowest bit off, so the list comes out least-significant first.
        bits.append(x & 1)
        x = x >> 1
    result = 0
    for b in bits:
        #> Reading that list forwards while shifting left writes it backwards,
        #> which is exactly the reversal.
        result = (result << 1) | b
    return result


APPROACHES = [
    {"id": "collect", "label": "Collect the bits, rebuild", "fn": collect_then_rebuild,
     "complexity": {"time": "O(32)", "space": "O(32)"},
     "viz": {"bits": "bits"}},
    {"id": "shift", "label": "Shift bits across", "fn": shift_across,
     "complexity": {"time": "O(32)", "space": "O(1)"},
     "viz": {}},
]
