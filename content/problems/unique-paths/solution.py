META = {
    "slug": "unique-paths",
    "title": "Unique Paths",
    "pattern": "2-D Dynamic Programming",
    "difficulty": "Medium",
    "leetcode": 62,
    "prompt": (
        "A robot starts in the top-left cell of an m x n grid and can only move "
        "right or down. Count the distinct paths to the bottom-right cell."
    ),
    "examples": [
        {"input": "m = 3, n = 7", "output": "28"},
        {"input": "m = 3, n = 2", "output": "3",
         "why": "Down-down-right, down-right-down, and right-down-down."},
    ],
    "constraints": ["1 <= m, n <= 100"],
}

VARIANTS = [
    {"id": "typical", "label": "4 x 5", "input": {"rows": 4, "cols": 5}},
    {"id": "edge", "label": "Single row", "input": {"rows": 1, "cols": 6}},
    {"id": "worst-case", "label": "6 x 6", "input": {"rows": 6, "cols": 6}},
]


def table(rows, cols):
    #> Every cell in the top row is reachable only by walking right the whole way,
    #> and every cell in the left column only by walking down. One path each.
    dp = [[1] * cols for _ in range(rows)]
    for r in range(1, rows):
        for c in range(1, cols):
            #> Any other cell is entered from above or from the left, never both at
            #> once, so its count is just those two counts added together.
            dp[r][c] = dp[r - 1][c] + dp[r][c - 1]
    return dp[rows - 1][cols - 1]


def one_row(rows, cols):
    #> The recurrence only ever looks one row back, so one row of memory is enough.
    row = [1] * cols
    for r in range(1, rows):
        for c in range(1, cols):
            #> row[c] still holds the row above; row[c-1] already holds this row.
            #> Reading both in this order is what makes the single array work.
            row[c] = row[c] + row[c - 1]
    return row[cols - 1]


APPROACHES = [
    {
        "id": "table",
        "label": "Full table",
        "fn": table,
        "complexity": {"time": "O(mn)", "space": "O(mn)"},
        "viz": {"dp": "grid", "r": "row:dp", "c": "col:dp"},
    },
    {
        "id": "one-row",
        "label": "Rolling row",
        "fn": one_row,
        "complexity": {"time": "O(mn)", "space": "O(n)"},
        "viz": {"row": "array", "c": "pointer:row"},
    },
]
