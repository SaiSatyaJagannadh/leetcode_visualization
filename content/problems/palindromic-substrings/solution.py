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


APPROACHES = [
    {"id": "expand", "label": "Count every expansion", "fn": expand_around_centre,
     "complexity": {"time": "O(n²)", "space": "O(1)"},
     "viz": {"s": "array", "i": "pointer:s", "lo": "pointer:s", "hi": "pointer:s"}},
]
