META = {
    "slug": "swim-in-rising-water",
    "title": "Swim in Rising Water",
    "pattern": "Advanced Graphs",
    "difficulty": "Hard",
    "leetcode": 778,
    "prompt": "Water rises over a grid of heights. You may move to a neighbouring cell once the water level is at least as high as both cells. Return the earliest time you can reach the bottom-right corner from the top-left.",
    "examples": [
        {"input": "grid = [[0,2],[1,3]]", "output": "3"},
        {"input": "grid = [[0,1,2],[3,4,5],[6,7,8]]", "output": "8"},
    ],
    "constraints": ["1 <= n <= 50", "Heights are a permutation of 0 .. n²-1"],
}

A = [[0, 2], [1, 3]]
B = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]

VARIANTS = [
    {"id": "typical", "label": "2 x 2", "input": lambda: {"grid": [r[:] for r in A]}},
    {"id": "edge", "label": "Single cell", "input": lambda: {"grid": [[0]]}},
    {"id": "worst-case", "label": "3 x 3", "input": lambda: {"grid": [r[:] for r in B]}},
]

BIG = 10 ** 9


def widest_path(grid):
    n = len(grid)
    #> Like Dijkstra, except the cost of a path isn't its sum but its *maximum*
    #> cell — the moment the water first got high enough to clear every step.
    best = [[BIG] * n for _ in range(n)]
    best[0][0] = grid[0][0]
    done = {}
    while True:
        #> Settle the reachable cell with the lowest required water level.
        pr, pc, pv = -1, -1, BIG
        for r in range(n):
            for c in range(n):
                key = str(r) + "," + str(c)
                if key not in done and best[r][c] < pv:
                    pr, pc, pv = r, c, best[r][c]
        if pr == -1:
            break
        done[str(pr) + "," + str(pc)] = True
        for d in ([1, 0], [-1, 0], [0, 1], [0, -1]):
            nr, nc = pr + d[0], pc + d[1]
            if 0 <= nr < n and 0 <= nc < n:
                #> Stepping there needs the water at least as high as both cells.
                need = max(pv, grid[nr][nc])
                if need < best[nr][nc]:
                    best[nr][nc] = need
    return best[n - 1][n - 1]


APPROACHES = [
    {"id": "widest", "label": "Dijkstra on the path maximum", "fn": widest_path,
     "complexity": {"time": "O(n⁴)", "space": "O(n²)"},
     "viz": {"grid": "grid", "best": "grid", "pr": "row:best", "pc": "col:best"}},
]
