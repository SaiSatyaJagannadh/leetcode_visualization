META = {
    "slug": "decode-ways",
    "title": "Decode Ways",
    "pattern": "1-D Dynamic Programming",
    "difficulty": "Medium",
    "leetcode": 91,
    "prompt": "Letters A to Z map to 1 to 26. Given a string of digits, count the ways it can be read back as letters.",
    "examples": [
        {"input": 's = "226"', "output": "3", "why": "BBF, BZ, or VF."},
        {"input": 's = "06"', "output": "0", "why": "A leading zero decodes to nothing."},
    ],
    "constraints": ["1 <= len(s) <= 100", "Digits only"],
}

VARIANTS = [
    {"id": "typical", "label": "Three ways", "input": {"s": "226"}},
    {"id": "edge", "label": "Leading zero", "input": {"s": "06"}},
    {"id": "worst-case", "label": "Zero mid-string", "input": {"s": "1201"}},
]


def bottom_up(s):
    #> ways[i] counts the readings of the first i digits. ways[0] is 1 because
    #> the empty prefix has exactly one reading: nothing.
    ways = [0] * (len(s) + 1)
    ways[0] = 1
    for i in range(1, len(s) + 1):
        #> A single digit works unless it's 0, which has no letter.
        if s[i - 1] != "0":
            ways[i] += ways[i - 1]
        #> A pair works only in the range 10 to 26, and never with a leading 0.
        if i >= 2 and "10" <= s[i - 2:i] <= "26":
            ways[i] += ways[i - 2]
    return ways[len(s)]


MEMO = {}


def top_down(s):
    #> Same recurrence read forwards: from position i, how many ways are there
    #> to read the rest? The memo is what keeps it linear.
    MEMO.clear()
    return _from(s, 0)


def _from(s, i):
    if i == len(s):
        #> Consumed the whole string, so the choices made getting here are one
        #> valid reading.
        return 1
    if s[i] == "0":
        #> No letter is encoded by a leading zero, so this branch is dead.
        return 0
    if i in MEMO:
        return MEMO[i]
    #> Take one digit as a letter.
    total = _from(s, i + 1)
    #> Or take two, if they land in the 10..26 range that has a letter.
    if i + 1 < len(s) and "10" <= s[i:i + 2] <= "26":
        total += _from(s, i + 2)
    MEMO[i] = total
    return total


APPROACHES = [
    {"id": "top-down", "label": "Recursion with a memo", "fn": top_down,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"s": "array", "MEMO": "map", "$calls": "recursion"}},
    {"id": "bottom-up", "label": "One or two digits at a time", "fn": bottom_up,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"s": "array", "ways": "array", "i": "pointer:ways"}},
]
