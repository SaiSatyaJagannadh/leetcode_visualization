META = {
    "slug": "minimum-window-substring",
    "title": "Minimum Window Substring",
    "pattern": "Sliding Window",
    "difficulty": "Hard",
    "leetcode": 76,
    "prompt": "Return the shortest substring of s that contains every character of t, counting repeats. If no such window exists, return the empty string.",
    "examples": [
        {"input": 's = "ADOBECODEBANC", t = "ABC"', "output": '"BANC"'},
        {"input": 's = "a", t = "aa"', "output": '""', "why": "s has only one a but two are needed."},
    ],
    "constraints": ["1 <= len(s), len(t) <= 10^5"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"s": "ADOBECAB", "t": "ABC"}},
    {"id": "edge", "label": "Impossible", "input": {"s": "a", "t": "aa"}},
    {"id": "worst-case", "label": "Whole string needed", "input": {"s": "abc", "t": "abc"}},
]


def sliding_window(s, t):
    need = {}
    for ch in t:
        need[ch] = need.get(ch, 0) + 1
    #> missing counts how many required characters the window is still short of.
    missing = len(t)
    lo = 0
    best = ""
    for hi in range(len(s)):
        ch = s[hi]
        if need.get(ch, 0) > 0:
            #> Only a character we still owe reduces the debt; extras don't.
            missing -= 1
        need[ch] = need.get(ch, 0) - 1
        while missing == 0:
            #> The window is valid. Record it if it beats the best, then try to
            #> shrink from the left — a valid window is only interesting if small.
            if best == "" or hi - lo + 1 < len(best):
                best = s[lo:hi + 1]
            need[s[lo]] = need[s[lo]] + 1
            if need[s[lo]] > 0:
                #> Dropping this one breaks the window, so the debt returns.
                missing += 1
            lo += 1
    return best


APPROACHES = [
    {"id": "window", "label": "Grow then shrink", "fn": sliding_window,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"s": "array", "lo": "pointer:s", "hi": "pointer:s", "need": "map"}},
]
