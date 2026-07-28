META = {
    "slug": "permutation-in-string",
    "title": "Permutation in String",
    "pattern": "Sliding Window",
    "difficulty": "Medium",
    "leetcode": 567,
    "prompt": "Decide whether the second string contains any rearrangement of the first as a contiguous substring.",
    "examples": [
        {"input": 's1 = "ab", s2 = "eidbaooo"', "output": "true", "why": '"ba" is a rearrangement of "ab".'},
        {"input": 's1 = "ab", s2 = "eidboaoo"', "output": "false",
         "why": "The a and b never sit next to each other."},
    ],
    "constraints": ["1 <= len(s1), len(s2) <= 10^4", "Lowercase English letters"],
}

VARIANTS = [
    {"id": "typical", "label": "Found", "input": {"s1": "ab", "s2": "eidbaooo"}},
    {"id": "edge", "label": "Not found", "input": {"s1": "ab", "s2": "eidboaoo"}},
    {"id": "worst-case", "label": "Match at the very end", "input": {"s1": "abc", "s2": "xxxcba"}},
]


def fixed_window(s1, s2):
    if len(s1) > len(s2):
        return False
    #> A rearrangement has exactly the same letter counts, so the window never
    #> needs to change size — only slide.
    need = {}
    for ch in s1:
        need[ch] = need.get(ch, 0) + 1
    have = {}
    for i in range(len(s2)):
        ch = s2[i]
        have[ch] = have.get(ch, 0) + 1
        if i >= len(s1):
            #> Drop the character falling out of the left edge as we slide.
            out = s2[i - len(s1)]
            have[out] -= 1
            if have[out] == 0:
                del have[out]
        if have == need:
            #> Identical tallies means this window is a rearrangement of s1.
            return True
    return False


APPROACHES = [
    {"id": "fixed-window", "label": "Fixed-width window", "fn": fixed_window,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"s2": "array", "i": "pointer:s2", "need": "map", "have": "map"}},
]
