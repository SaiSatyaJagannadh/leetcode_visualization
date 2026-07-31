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


def precompute_then_cut(s):
    #> Work out once, for every pair of positions, whether that slice is a
    #> palindrome. The recursion then never re-tests a slice — the backtracking
    #> version re-checks the same pieces on every branch that reaches them.
    n = len(s)
    ok = [[False] * n for _ in range(n)]
    for lo in range(n - 1, -1, -1):
        for hi in range(lo, n):
            #> A slice is a palindrome when its ends match and the inside was
            #> already known to be one — which is why lo counts downward.
            if s[lo] == s[hi] and (hi - lo < 2 or ok[lo + 1][hi - 1]):
                ok[lo][hi] = True
    out = []
    _cut(s, ok, 0, [], out)
    return out


def _cut(s, ok, start, current, out):
    if start == len(s):
        out.append(list(current))
        return
    for end in range(start, len(s)):
        #> One table lookup instead of comparing the slice character by character.
        if ok[start][end]:
            current.append(s[start:end + 1])
            _cut(s, ok, end + 1, current, out)
            current.pop()


APPROACHES = [
    {"id": "precompute", "label": "Table the palindromes first", "fn": precompute_then_cut,
     "complexity": {"time": "O(n \u00b7 2\u207f)", "space": "O(n\u00b2)"},
     "viz": {"s": "array", "ok": "grid", "current": "stack", "out": "queue", "$calls": "recursion"}},
    {"id": "backtrack", "label": "Cut, check, recurse", "fn": backtrack,
     "complexity": {"time": "O(n · 2ⁿ)", "space": "O(n)"},
     "viz": {"s": "array", "current": "stack", "out": "queue", "$calls": "recursion"}},
]
