META = {
    "slug": "interleaving-string",
    "title": "Interleaving String",
    "pattern": "2-D Dynamic Programming",
    "difficulty": "Medium",
    "leetcode": 97,
    "prompt": "Decide whether the third string can be formed by shuffling the first two together while each keeps its own order.",
    "examples": [
        {"input": 's1 = "aab", s2 = "axy", s3 = "aaxaby"', "output": "true"},
        {"input": 's1 = "ab", s2 = "cd", s3 = "abcde"', "output": "false", "why": "Lengths don't add up."},
    ],
    "constraints": ["0 <= len(s1), len(s2) <= 100"],
}

VARIANTS = [
    {"id": "typical", "label": "Interleaves", "input": {"a": "aab", "b": "axy", "c": "aaxaby"}},
    {"id": "edge", "label": "Wrong length", "input": {"a": "ab", "b": "cd", "c": "abcde"}},
    {"id": "worst-case", "label": "Nearly works", "input": {"a": "aa", "b": "ab", "c": "aaba"}},
]


def table(a, b, c):
    if len(a) + len(b) != len(c):
        #> The lengths must add exactly, and checking first avoids a pointless grid.
        return False
    #> dp[i][j] asks whether the first i of a and first j of b can build the
    #> first i + j of c. The position in c is implied, which is why one grid is
    #> enough rather than three nested loops.
    dp = [[False] * (len(b) + 1) for _ in range(len(a) + 1)]
    dp[0][0] = True
    for i in range(len(a) + 1):
        for j in range(len(b) + 1):
            if i > 0 and dp[i - 1][j] and a[i - 1] == c[i + j - 1]:
                dp[i][j] = True  #> This character of c came from a.
            if j > 0 and dp[i][j - 1] and b[j - 1] == c[i + j - 1]:
                dp[i][j] = True  #> Or from b — either origin is enough.
    return dp[len(a)][len(b)]


APPROACHES = [
    {"id": "table", "label": "Fill the grid", "fn": table,
     "complexity": {"time": "O(mn)", "space": "O(mn)"},
     "viz": {"dp": "grid", "i": "row:dp", "j": "col:dp"}},
]
