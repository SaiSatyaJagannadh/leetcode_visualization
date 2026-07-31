META = {
    "slug": "word-break",
    "title": "Word Break",
    "pattern": "1-D Dynamic Programming",
    "difficulty": "Medium",
    "leetcode": 139,
    "prompt": "Decide whether a string can be cut into a sequence of dictionary words. Words may be reused.",
    "examples": [
        {"input": 's = "leetcode", words = ["leet","code"]', "output": "true"},
        {"input": 's = "catsandog", words = ["cats","dog","sand","and","cat"]', "output": "false"},
    ],
    "constraints": ["1 <= len(s) <= 300", "1 <= len(words) <= 1000"],
}

VARIANTS = [
    {"id": "typical", "label": "Breakable", "input": {"s": "leetcode", "words": ["leet", "code"]}},
    {"id": "edge", "label": "Not breakable", "input": {"s": "catsandog", "words": ["cats", "dog", "sand", "and", "cat"]}},
    {"id": "worst-case", "label": "Needs the shorter cut", "input": {"s": "aaab", "words": ["a", "aa", "b"]}},
]


def bottom_up(s, words):
    #> ok[i] means "the first i characters can be built". ok[0] is true because
    #> an empty prefix needs no words, and that seeds everything else.
    ok = [False] * (len(s) + 1)
    ok[0] = True
    for i in range(1, len(s) + 1):
        for w in words:
            #> If the prefix before this word was buildable and the word lands
            #> exactly here, then this longer prefix is buildable too.
            if i >= len(w) and ok[i - len(w)] and s[i - len(w):i] == w:
                ok[i] = True
                break
    return ok[len(s)]


MEMO = {}


def top_down(s, words):
    #> Asked from the front: can the rest be built starting at position i? The
    #> memo is doing the same job as the table, filled only where needed.
    MEMO.clear()
    return _from(s, words, 0)


def _from(s, words, i):
    if i == len(s):
        #> Consumed the whole string, so the cuts made getting here all worked.
        return True
    if i in MEMO:
        return MEMO[i]
    MEMO[i] = False
    for w in words:
        #> Try each word as the next piece. Only one has to lead anywhere.
        if s[i:i + len(w)] == w and _from(s, words, i + len(w)):
            MEMO[i] = True
            break
    return MEMO[i]


APPROACHES = [
    {"id": "top-down", "label": "Can the rest be built?", "fn": top_down,
     "complexity": {"time": "O(n \u00b7 w \u00b7 L)", "space": "O(n)"},
     "viz": {"s": "array", "words": "array", "MEMO": "map", "$calls": "recursion"}},
    {"id": "bottom-up", "label": "Buildable prefixes", "fn": bottom_up,
     "complexity": {"time": "O(n · w · L)", "space": "O(n)"},
     "viz": {"s": "array", "ok": "array", "i": "pointer:ok", "words": "array"}},
]
