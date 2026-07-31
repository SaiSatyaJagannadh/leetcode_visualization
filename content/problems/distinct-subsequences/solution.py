META = {
    "slug": "distinct-subsequences",
    "title": "Distinct Subsequences",
    "pattern": "2-D Dynamic Programming",
    "difficulty": "Hard",
    "leetcode": 115,
    "prompt": "Count the distinct ways the second string appears as a subsequence of the first — characters in order, not necessarily adjacent.",
    "examples": [
        {"input": 's = "rabbbit", t = "rabbit"', "output": "3"},
        {"input": 's = "abc", t = "abcd"', "output": "0"},
    ],
    "constraints": ["1 <= len(s), len(t) <= 1000"],
}

VARIANTS = [
    {"id": "typical", "label": "Three ways", "input": {"s": "rabbbit", "t": "rabbit"}},
    {"id": "edge", "label": "Target too long", "input": {"s": "abc", "t": "abcd"}},
    {"id": "worst-case", "label": "All identical", "input": {"s": "aaa", "t": "aa"}},
]


def table(s, t):
    #> dp[i][j] counts how many ways the first j characters of t can be found in
    #> the first i of s. Column 0 is 1 everywhere: the empty target is always
    #> matched exactly once, by taking nothing.
    dp = [[0] * (len(t) + 1) for _ in range(len(s) + 1)]
    for i in range(len(s) + 1):
        dp[i][0] = 1
    for i in range(1, len(s) + 1):
        for j in range(1, len(t) + 1):
            #> Skipping this character of s is always an option.
            dp[i][j] = dp[i - 1][j]
            if s[i - 1] == t[j - 1]:
                #> And when they match, using it is a second, separate option —
                #> so the two counts add rather than replacing each other.
                dp[i][j] += dp[i - 1][j - 1]
    return dp[len(s)][len(t)]


CACHE = {}


def top_down(s, t):
    #> Read as a choice instead of a table: at each character of s, skip it, or
    #> use it when it matches. The count is the number of ways to reach the end.
    CACHE.clear()
    return _count(s, t, 0, 0)


def _count(s, t, i, j):
    if j == len(t):
        #> The whole target is matched, so the path taken here is one way.
        return 1
    if i == len(s):
        #> Ran out of source with target left over.
        return 0
    key = str(i) + ":" + str(j)
    if key in CACHE:
        return CACHE[key]
    #> Skipping this character of s is always allowed.
    total = _count(s, t, i + 1, j)
    if s[i] == t[j]:
        #> A match adds a second, separate way rather than replacing the first —
        #> which is why the table version adds instead of taking a maximum.
        total += _count(s, t, i + 1, j + 1)
    CACHE[key] = total
    return total


APPROACHES = [
    {"id": "top-down", "label": "Skip it or use it", "fn": top_down,
     "complexity": {"time": "O(mn)", "space": "O(mn)"},
     "viz": {"s": "array", "t": "array", "CACHE": "map", "$calls": "recursion"}},
    {"id": "table", "label": "Fill the grid", "fn": table,
     "complexity": {"time": "O(mn)", "space": "O(mn)"},
     "viz": {"dp": "grid", "i": "row:dp", "j": "col:dp", "s": "array", "t": "array"}},
]
