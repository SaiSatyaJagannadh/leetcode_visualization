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


def try_every_window(s, k):
    #> Every start, every end, counted from scratch. The sliding window works
    #> because a window never has to shrink below where it already got to —
    #> this version throws that away and recounts each time.
    best = 0
    for lo in range(len(s)):
        counts = {}
        most = 0
        for hi in range(lo, len(s)):
            ch = s[hi]
            counts[ch] = counts.get(ch, 0) + 1
            if counts[ch] > most:
                most = counts[ch]
            #> Legal only if the non-dominant letters fit inside the k rewrites.
            if (hi - lo + 1) - most <= k and hi - lo + 1 > best:
                best = hi - lo + 1
    return best


APPROACHES = [
    {"id": "brute-force", "label": "Every window, recounted", "fn": try_every_window,
     "complexity": {"time": "O(n\u00b2)", "space": "O(1)"},
     "viz": {"s": "array", "counts": "map", "lo": "pointer:s", "hi": "pointer:s"}},
    {"id": "window", "label": "Sliding window", "fn": sliding_window,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"s": "array", "lo": "pointer:s", "hi": "pointer:s", "counts": "map"}},
]
