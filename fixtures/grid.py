"""A DP table filling row by row, and a BFS flood fill with a live frontier."""

META = {"slug": "_grid", "title": "Grid renderer", "pattern": "Fixture"}

VARIANTS = [
    {"id": "typical", "label": "4 x 5", "input": {"rows": 4, "cols": 5}},
    {"id": "edge", "label": "Single row", "input": {"rows": 1, "cols": 6}},
]


def unique_paths(rows, cols):
    #> Every cell in the top row and left column has exactly one way in.
    dp = [[1] * cols for _ in range(rows)]
    for r in range(1, rows):
        for c in range(1, cols):
            #> Any other cell is reached from above or from the left, never both.
            dp[r][c] = dp[r - 1][c] + dp[r][c - 1]
    return dp[rows - 1][cols - 1]


def flood(rows, cols):
    grid = [[0] * cols for _ in range(rows)]
    frontier = [[0, 0]]  #> The frontier holds every cell discovered but not yet expanded.
    seen = 0
    while frontier:
        nxt = []
        seen += 1
        for cell in frontier:
            r, c = cell[0], cell[1]
            grid[r][c] = seen  #> Colour by the ring it was reached on.
            for d in ([1, 0], [0, 1], [-1, 0], [0, -1]):
                nr, nc = r + d[0], c + d[1]
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                    if [nr, nc] not in nxt:
                        nxt.append([nr, nc])
        #> One whole ring expands per outer pass — that is what makes BFS level order.
        frontier = nxt
    return seen


APPROACHES = [
    {
        "id": "dp",
        "label": "DP table",
        "fn": unique_paths,
        "complexity": {"time": "O(rc)", "space": "O(rc)"},
        "viz": {"dp": "grid", "r": "row:dp", "c": "col:dp"},
    },
    {
        "id": "bfs",
        "label": "BFS flood fill",
        "fn": flood,
        "complexity": {"time": "O(rc)", "space": "O(rc)"},
        "viz": {"grid": "grid", "frontier": "cells:grid", "nxt": "array"},
    },
]
