META = {
    "slug": "palindrome-partitioning",
    "title": "Palindrome Partitioning",
    "pattern": "Backtracking",
    "difficulty": "Medium",
    "leetcode": 131,
    "prompt": "Cut a string into pieces so that every piece reads the same forwards and backwards. Return every possible way to cut it.",
    "examples": [
        {"input": 's = "aab"', "output": '[["a","a","b"],["aa","b"]]'},
        {"input": 's = "a"', "output": '[["a"]]'},
    ],
    "constraints": ["1 <= len(s) <= 16"],
    "unordered": True,
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"s": "aab"}},
    {"id": "edge", "label": "Single letter", "input": {"s": "a"}},
    {"id": "worst-case", "label": "All the same", "input": {"s": "aaa"}},
]


def backtrack(s, start=0, current=None, out=None):
    if current is None:
        current, out = [], []
    if start == len(s):
        #> Consumed the whole string, so this set of cuts is valid.
        out.append(list(current))
        return out
    for end in range(start + 1, len(s) + 1):
        piece = s[start:end]
        #> Only take this cut if the piece itself is a palindrome; otherwise the
        #> entire subtree below it is invalid and worth skipping outright.
        if piece == piece[::-1]:
            current.append(piece)
            backtrack(s, end, current, out)
            current.pop()
    return out


APPROACHES = [
    {"id": "backtrack", "label": "Cut, check, recurse", "fn": backtrack,
     "complexity": {"time": "O(n · 2ⁿ)", "space": "O(n)"},
     "viz": {"s": "array", "current": "stack", "out": "queue", "$calls": "recursion"}},
]
