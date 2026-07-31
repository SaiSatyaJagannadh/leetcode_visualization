META = {
    "slug": "palindromic-substrings",
    "title": "Palindromic Substrings",
    "pattern": "1-D Dynamic Programming",
    "difficulty": "Medium",
    "leetcode": 647,
    "prompt": "Count how many substrings read the same forwards and backwards. Substrings at different positions count separately even when identical.",
    "examples": [
        {"input": 's = "abc"', "output": "3", "why": "Each single character."},
        {"input": 's = "aaa"', "output": "6", "why": '"a" three times, "aa" twice, "aaa" once.'},
    ],
    "constraints": ["1 <= len(s) <= 1000"],
}

VARIANTS = [
    {"id": "typical", "label": "No repeats", "input": {"s": "abc"}},
    {"id": "edge", "label": "All same", "input": {"s": "aaa"}},
    {"id": "worst-case", "label": "Mixed", "input": {"s": "abba"}},
]


def expand_around_centre(s):
    count = 0
    for i in range(len(s)):
        for offset in (0, 1):
            lo = i
            hi = i + offset
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                #> Every successful expansion is itself one more palindrome, so
                #> counting happens inside the loop rather than after it.
                count += 1
                lo -= 1
                hi += 1
    return count


def check_every_substring(s):
    #> Count by testing rather than by expanding. Every substring gets its own
    #> symmetry check, so the same character pairs are compared again and again —
    #> the expansion reuses that work by construction.
    count = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            if _mirrored(s, i, j):
                count += 1
    return count


def _mirrored(s, lo, hi):
    while lo < hi:
        #> One mismatch rules this substring out entirely.
        if s[lo] != s[hi]:
            return False
        lo += 1
        hi -= 1
    return True


APPROACHES = [
    {"id": "brute-force", "label": "Test every substring", "fn": check_every_substring,
     "complexity": {"time": "O(n\u00b3)", "space": "O(1)"},
     "viz": {"s": "array", "i": "pointer:s", "j": "pointer:s"}},
    {"id": "expand", "label": "Count every expansion", "fn": expand_around_centre,
     "complexity": {"time": "O(n²)", "space": "O(1)"},
     "viz": {"s": "array", "i": "pointer:s", "lo": "pointer:s", "hi": "pointer:s"}},
]
