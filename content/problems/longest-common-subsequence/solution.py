META = {
    "slug": "longest-common-subsequence",
    "title": "Longest Common Subsequence",
    "pattern": "2-D Dynamic Programming",
    "difficulty": "Medium",
    "leetcode": 1143,
    "prompt": "Return the length of the longest sequence of characters appearing in both strings in the same order, though not necessarily adjacent.",
    "examples": [
        {"input": 'text1 = "abcde", text2 = "ace"', "output": "3", "why": '"ace".'},
        {"input": 'text1 = "abc", text2 = "def"', "output": "0"},
    ],
    "constraints": ["1 <= len(text1), len(text2) <= 1000"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"a": "abcde", "b": "ace"}},
    {"id": "edge", "label": "Nothing shared", "input": {"a": "abc", "b": "def"}},
    {"id": "worst-case", "label": "Identical", "input": {"a": "abcd", "b": "abcd"}},
]


def table(a, b):
    #> dp[i][j] answers the question for the first i of a and first j of b. Row 0
    #> and column 0 are zero because an empty string shares nothing.
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                #> Matching characters can both be spent, extending the diagonal.
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                #> Otherwise drop one character from one string and keep the best.
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[len(a)][len(b)]


APPROACHES = [
    {"id": "table", "label": "Fill the grid", "fn": table,
     "complexity": {"time": "O(mn)", "space": "O(mn)"},
     "viz": {"dp": "grid", "i": "row:dp", "j": "col:dp", "a": "array", "b": "array"}},
]
