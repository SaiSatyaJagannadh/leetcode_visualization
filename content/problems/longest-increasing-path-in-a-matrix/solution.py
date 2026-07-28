META = {
    "slug": "longest-increasing-path-in-a-matrix",
    "title": "Longest Increasing Path in a Matrix",
    "pattern": "2-D Dynamic Programming",
    "difficulty": "Hard",
    "leetcode": 329,
    "prompt": "Find the longest path through the grid where each step moves to a horizontally or vertically adjacent cell holding a strictly larger value.",
    "examples": [
        {"input": "matrix = [[9,9,4],[6,6,8],[2,1,1]]", "output": "4", "why": "1 → 2 → 6 → 9."},
        {"input": "matrix = [[1]]", "output": "1"},
    ],
    "constraints": ["1 <= rows, cols <= 200"],
}

A = [[9, 9, 4], [6, 6, 8], [2, 1, 1]]

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": lambda: {"matrix": [r[:] for r in A]}},
    {"id": "edge", "label": "Single cell", "input": lambda: {"matrix": [[1]]}},
    {"id": "worst-case", "label": "All equal", "input": lambda: {"matrix": [[3, 3], [3, 3]]}},
]


def memoised(matrix):
    rows, cols = len(matrix), len(matrix[0])
    #> memo[r][c] is the longest path starting at that cell. Because every step
    #> must strictly increase, no path can revisit a cell, so there are no cycles
    #> and each cell's answer is fixed — which is what makes memoising valid.
    memo = [[0] * cols for _ in range(rows)]
    best = 0
    for r in range(rows):
        for c in range(cols):
            best = max(best, _walk(matrix, r, c, memo))
    return best


def _walk(matrix, r, c, memo):
    if memo[r][c] != 0:
        #> Already solved on an earlier start; reuse it rather than re-exploring.
        return memo[r][c]
    longest = 1
    for d in ([1, 0], [-1, 0], [0, 1], [0, -1]):
        nr, nc = r + d[0], c + d[1]
        if 0 <= nr < len(matrix) and 0 <= nc < len(matrix[0]):
            if matrix[nr][nc] > matrix[r][c]:
                longest = max(longest, 1 + _walk(matrix, nr, nc, memo))
    memo[r][c] = longest
    return longest


APPROACHES = [
    {"id": "memo", "label": "DFS with memoisation", "fn": memoised,
     "complexity": {"time": "O(rc)", "space": "O(rc)"},
     "viz": {"matrix": "grid", "memo": "grid", "$calls": "recursion"}},
]
