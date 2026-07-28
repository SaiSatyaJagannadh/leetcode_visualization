META = {
    "slug": "longest-substring-without-repeating-characters",
    "title": "Longest Substring Without Repeating Characters",
    "pattern": "Sliding Window",
    "difficulty": "Medium",
    "leetcode": 3,
    "prompt": (
        "Find the length of the longest stretch of a string in which no character "
        "appears twice."
    ),
    "examples": [
        {"input": 's = "abcabcbb"', "output": "3", "why": '"abc" is the longest clean run.'},
        {"input": 's = "bbbbb"', "output": "1", "why": "Every character repeats immediately."},
        {"input": 's = "pwwkew"', "output": "3", "why": '"wke" — note "pwke" is not contiguous.'},
    ],
    "constraints": ["0 <= len(s) <= 5 * 10^4"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"s": "abcabcbb"}},
    {"id": "edge", "label": "All same", "input": {"s": "bbbbb"}},
    {"id": "worst-case", "label": "Repeat inside", "input": {"s": "pwwkew"}},
]


def brute_force(s):
    best = 0
    for i in range(len(s)):
        seen = []
        for j in range(i, len(s)):
            if s[j] in seen:
                break  #> This run is dead; restart from the next i.
            seen.append(s[j])
            if len(seen) > best:
                best = len(seen)
    return best


def sliding_window(s):
    #> The window is s[lo..hi]. Its contents are always duplicate-free.
    last = {}
    lo = 0
    best = 0
    for hi in range(len(s)):
        ch = s[hi]
        if ch in last and last[ch] >= lo:
            #> This character is already inside the window, so the window has to
            #> shrink past its previous position. Jumping straight there — rather
            #> than stepping — is what keeps this linear.
            lo = last[ch] + 1
        last[ch] = hi  #> Remember where this character was most recently seen.
        if hi - lo + 1 > best:
            best = hi - lo + 1  #> A longer clean stretch than anything before.
    return best


APPROACHES = [
    {
        "id": "brute-force",
        "label": "Every start",
        "fn": brute_force,
        "complexity": {"time": "O(n²)", "space": "O(n)"},
        "viz": {"s": "array", "i": "pointer:s", "j": "pointer:s", "seen": "stack"},
    },
    {
        "id": "sliding-window",
        "label": "Sliding window",
        "fn": sliding_window,
        "complexity": {"time": "O(n)", "space": "O(n)"},
        "viz": {"s": "array", "lo": "pointer:s", "hi": "pointer:s"},
    },
]
