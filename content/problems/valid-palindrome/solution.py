META = {
    "slug": "valid-palindrome",
    "title": "Valid Palindrome",
    "pattern": "Two Pointers",
    "difficulty": "Easy",
    "leetcode": 125,
    "prompt": "Ignoring case and every non-alphanumeric character, decide whether the string reads the same forwards and backwards.",
    "examples": [
        {"input": 's = "A man, a plan, a canal: Panama"', "output": "true",
         "why": 'Stripped down it is "amanaplanacanalpanama".'},
        {"input": 's = "race a car"', "output": "false"},
    ],
    "constraints": ["1 <= len(s) <= 2 * 10^5"],
}

VARIANTS = [
    {"id": "typical", "label": "With punctuation", "input": {"s": "A man, a plan!"}},
    {"id": "edge", "label": "Not a palindrome", "input": {"s": "race a car"}},
    {"id": "worst-case", "label": "Fails at the middle", "input": {"s": "abcxcba"}},
]


def build_reverse(s):
    #> Strip to the characters that count, lowercased.
    clean = []
    for ch in s:
        if ch.isalnum():
            clean.append(ch.lower())
    #> Then just compare it against itself backwards. Clear, but it copies the string.
    back = list(reversed(clean))
    return clean == back


def two_pointers(s):
    lo = 0
    hi = len(s) - 1
    while lo < hi:
        #> Skip anything that isn't a letter or digit, from whichever end.
        if not s[lo].isalnum():
            lo += 1
        elif not s[hi].isalnum():
            hi -= 1
        elif s[lo].lower() != s[hi].lower():
            #> A mismatched pair settles it; nothing further in can rescue it.
            return False
        else:
            #> Matched, so close in from both ends at once.
            lo += 1
            hi -= 1
    #> The pointers met without ever disagreeing.
    return True


APPROACHES = [
    {"id": "reverse", "label": "Clean and reverse", "fn": build_reverse,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"s": "array", "clean": "array", "back": "array"}},
    {"id": "two-pointers", "label": "Two pointers", "fn": two_pointers,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"s": "array", "lo": "pointer:s", "hi": "pointer:s"}},
]
