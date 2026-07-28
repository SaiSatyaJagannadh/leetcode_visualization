META = {
    "slug": "edit-distance",
    "title": "Edit Distance",
    "pattern": "2-D Dynamic Programming",
    "difficulty": "Medium",
    "leetcode": 72,
    "prompt": "Return the fewest single-character insertions, deletions or replacements needed to turn one word into the other.",
    "examples": [
        {"input": 'word1 = "horse", word2 = "ros"', "output": "3"},
        {"input": 'word1 = "", word2 = "abc"', "output": "3", "why": "Three insertions."},
    ],
    "constraints": ["0 <= len(word1), len(word2) <= 500"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"a": "horse", "b": "ros"}},
    {"id": "edge", "label": "One empty", "input": {"a": "", "b": "abc"}},
    {"id": "worst-case", "label": "Identical", "input": {"a": "abc", "b": "abc"}},
]


def table(a, b):
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    #> Turning a prefix into nothing costs one deletion per character, and the
    #> mirror for insertions. These edges seed the whole grid.
    for i in range(len(a) + 1):
        dp[i][0] = i
    for j in range(len(b) + 1):
        dp[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                #> Characters agree, so this position is free — carry the diagonal.
                dp[i][j] = dp[i - 1][j - 1]
            else:
                #> Otherwise pay one, for whichever of the three edits is cheapest:
                #> replace (diagonal), delete (up), or insert (left).
                dp[i][j] = 1 + min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1])
    return dp[len(a)][len(b)]


APPROACHES = [
    {"id": "table", "label": "Fill the grid", "fn": table,
     "complexity": {"time": "O(mn)", "space": "O(mn)"},
     "viz": {"dp": "grid", "i": "row:dp", "j": "col:dp", "a": "array", "b": "array"}},
]
