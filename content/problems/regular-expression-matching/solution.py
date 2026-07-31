META = {
    "slug": "regular-expression-matching",
    "title": "Regular Expression Matching",
    "pattern": "2-D Dynamic Programming",
    "difficulty": "Hard",
    "leetcode": 10,
    "prompt": "Match a string against a pattern where '.' matches any single character and '*' means zero or more of whatever precedes it. The match must cover the entire string.",
    "examples": [
        {"input": 's = "aab", p = "c*a*b"', "output": "true", "why": "c* matches nothing, a* matches aa."},
        {"input": 's = "mississippi", p = "mis*is*p*."', "output": "false"},
    ],
    "constraints": ["1 <= len(s) <= 20", "1 <= len(p) <= 20"],
}

VARIANTS = [
    {"id": "typical", "label": "Star matches zero", "input": {"s": "aab", "p": "c*a*b"}},
    {"id": "edge", "label": "No match", "input": {"s": "ab", "p": "a"}},
    {"id": "worst-case", "label": "Dot star", "input": {"s": "abc", "p": ".*c"}},
]


def table(s, p):
    #> dp[i][j] asks whether the first i of s match the first j of p.
    dp = [[False] * (len(p) + 1) for _ in range(len(s) + 1)]
    dp[0][0] = True
    #> An empty string can still match a pattern made only of x* groups, so seed
    #> the top row before the main loop.
    for j in range(1, len(p) + 1):
        if p[j - 1] == "*":
            dp[0][j] = dp[0][j - 2]
    for i in range(1, len(s) + 1):
        for j in range(1, len(p) + 1):
            if p[j - 1] == "*":
                #> Two independent options: drop the whole x* group (look two
                #> back), or consume one character of s and keep the group live.
                dp[i][j] = dp[i][j - 2]
                if p[j - 2] == "." or p[j - 2] == s[i - 1]:
                    dp[i][j] = dp[i][j] or dp[i - 1][j]
            elif p[j - 1] == "." or p[j - 1] == s[i - 1]:
                #> An ordinary character match just carries the diagonal forward.
                dp[i][j] = dp[i - 1][j - 1]
    return dp[len(s)][len(p)]


MEMO = {}


def top_down(s, p):
    #> The same rules asked from the front, which is where the star's two
    #> options read most naturally: use it zero times, or consume one character
    #> and stay on it.
    MEMO.clear()
    return _match(s, p, 0, 0)


def _match(s, p, i, j):
    if j == len(p):
        #> Pattern exhausted; this only worked if the string is too.
        return i == len(s)
    key = str(i) + ":" + str(j)
    if key in MEMO:
        return MEMO[key]
    here = i < len(s) and (p[j] == "." or p[j] == s[i])
    if j + 1 < len(p) and p[j + 1] == "*":
        #> Skip the whole x* group, or use it once more and stay put.
        out = _match(s, p, i, j + 2) or (here and _match(s, p, i + 1, j))
    else:
        #> Ordinary character: both sides advance together or it fails.
        out = here and _match(s, p, i + 1, j + 1)
    MEMO[key] = out
    return out


APPROACHES = [
    {"id": "top-down", "label": "Match from the front", "fn": top_down,
     "complexity": {"time": "O(mn)", "space": "O(mn)"},
     "viz": {"MEMO": "map", "$calls": "recursion"}},
    {"id": "table", "label": "Fill the grid", "fn": table,
     "complexity": {"time": "O(mn)", "space": "O(mn)"},
     "viz": {"dp": "grid", "i": "row:dp", "j": "col:dp"}},
]
