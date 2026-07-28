META = {
    "slug": "longest-repeating-character-replacement",
    "title": "Longest Repeating Character Replacement",
    "pattern": "Sliding Window",
    "difficulty": "Medium",
    "leetcode": 424,
    "prompt": "You may change up to k characters in the string to any other letter. Return the length of the longest run of one repeated letter you can produce.",
    "examples": [
        {"input": 's = "ABAB", k = 2', "output": "4", "why": "Change both A's to B, or both B's to A."},
        {"input": 's = "AABABBA", k = 1', "output": "4",
         "why": 'Changing one B gives "AABA" -> "AAAA" as a window of four.'},
    ],
    "constraints": ["1 <= len(s) <= 10^5", "0 <= k <= len(s)"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"s": "AABABBA", "k": 1}},
    {"id": "edge", "label": "No changes allowed", "input": {"s": "ABAB", "k": 0}},
    {"id": "worst-case", "label": "Whole string works", "input": {"s": "ABAB", "k": 2}},
]


def sliding_window(s, k):
    counts = {}
    lo = 0
    most = 0
    best = 0
    for hi in range(len(s)):
        ch = s[hi]
        counts[ch] = counts.get(ch, 0) + 1
        #> most is the count of the window's dominant letter.
        most = max(most, counts[ch])
        #> Everything that isn't the dominant letter has to be rewritten. If that
        #> costs more than k, the window is illegal and has to give ground.
        while (hi - lo + 1) - most > k:
            counts[s[lo]] -= 1
            lo += 1
        if hi - lo + 1 > best:
            best = hi - lo + 1  #> A legal window longer than any before it.
    return best


APPROACHES = [
    {"id": "window", "label": "Sliding window", "fn": sliding_window,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"s": "array", "lo": "pointer:s", "hi": "pointer:s", "counts": "map"}},
]
