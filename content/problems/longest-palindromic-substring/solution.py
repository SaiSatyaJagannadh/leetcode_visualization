META = {
    "slug": "longest-palindromic-substring",
    "title": "Longest Palindromic Substring",
    "pattern": "1-D Dynamic Programming",
    "difficulty": "Medium",
    "leetcode": 5,
    "prompt": "Return the longest contiguous stretch of the string that reads the same forwards and backwards.",
    "examples": [
        {"input": 's = "babad"', "output": '"bab"', "why": '"aba" is equally long and also accepted.'},
        {"input": 's = "cbbd"', "output": '"bb"'},
    ],
    "constraints": ["1 <= len(s) <= 1000"],
}

VARIANTS = [
    {"id": "typical", "label": "Odd centre", "input": {"s": "babad"}},
    {"id": "edge", "label": "Even centre", "input": {"s": "cbbd"}},
    {"id": "worst-case", "label": "Whole string", "input": {"s": "aaaa"}},
]


def expand_around_centre(s):
    best = ""
    for i in range(len(s)):
        #> A palindrome is defined by its centre, and there are only 2n - 1 of
        #> them: one on each character, one between each pair. Checking every
        #> substring instead would be a factor of n more work.
        for offset in (0, 1):
            lo = i
            hi = i + offset
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                #> Still mirrored, so push both edges outward.
                lo -= 1
                hi += 1
            #> The loop stopped one step past the match, hence lo + 1.
            found = s[lo + 1:hi]
            if len(found) > len(best):
                best = found
    return best


APPROACHES = [
    {"id": "expand", "label": "Expand around every centre", "fn": expand_around_centre,
     "complexity": {"time": "O(n²)", "space": "O(1)"},
     "viz": {"s": "array", "i": "pointer:s", "lo": "pointer:s", "hi": "pointer:s"}},
]
