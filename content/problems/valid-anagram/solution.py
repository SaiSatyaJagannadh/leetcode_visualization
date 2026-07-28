META = {
    "slug": "valid-anagram",
    "title": "Valid Anagram",
    "pattern": "Arrays & Hashing",
    "difficulty": "Easy",
    "leetcode": 242,
    "prompt": "Decide whether one string is a rearrangement of the other, using exactly the same letters the same number of times.",
    "examples": [
        {"input": 's = "anagram", t = "nagaram"', "output": "true"},
        {"input": 's = "rat", t = "car"', "output": "false", "why": "Different letters entirely."},
    ],
    "constraints": ["1 <= len(s), len(t) <= 5 * 10^4", "Lowercase English letters"],
}

VARIANTS = [
    {"id": "typical", "label": "Anagram", "input": {"s": "anagram", "t": "nagaram"}},
    {"id": "edge", "label": "Different lengths", "input": {"s": "ab", "t": "abc"}},
    {"id": "worst-case", "label": "Same letters, wrong counts", "input": {"s": "aabb", "t": "abbb"}},
]


def sort_both(s, t):
    if len(s) != len(t):
        #> Different lengths can never be anagrams, and this saves the sort.
        return False
    #> Sorting throws away order, which is exactly the thing anagrams disagree on.
    a = sorted(s)
    b = sorted(t)
    return a == b


def count_letters(s, t):
    if len(s) != len(t):
        return False
    #> Tally how many of each letter s uses.
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    for ch in t:
        if ch not in counts or counts[ch] == 0:
            #> t needs a letter that s has already run out of.
            return False
        #> Spend one of s's letters against this one of t's.
        counts[ch] -= 1
    #> Equal lengths plus nothing overspent means every count landed on zero.
    return True


APPROACHES = [
    {"id": "sort", "label": "Sort both", "fn": sort_both,
     "complexity": {"time": "O(n log n)", "space": "O(n)"},
     "viz": {"s": "array", "t": "array", "a": "array", "b": "array"}},
    {"id": "count", "label": "Letter counts", "fn": count_letters,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"s": "array", "t": "array"}},
]
