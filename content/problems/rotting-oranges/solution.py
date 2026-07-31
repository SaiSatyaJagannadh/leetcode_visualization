META = {
    "slug": "rotting-oranges",
    "title": "Rotting Oranges",
    "pattern": "Graphs",
    "difficulty": "Medium",
    "leetcode": 994,
    "prompt": "In a grid, 0 is empty, 1 is a fresh orange and 2 is a rotten one. Each minute, every fresh orange touching a rotten one turns rotten. Return the minutes until none are fresh, or -1 if some never rot.",
    "examples": [
        {"input": "grid = [[2,1,1],[1,1,0],[0,1,1]]", "output": "4"},
        {"input": "grid = [[2,1,1],[0,1,1],[1,0,1]]", "output": "-1",
         "why": "The bottom-left orange is cut off from the rot."},
    ],
    "constraints": ["1 <= rows, cols <= 10", "Each cell is 0, 1 or 2"],
}

A = [[2, 1, 1], [1, 1, 0], [0, 1, 1]]
B = [[2, 1, 0], [0, 1, 1]]

VARIANTS = [
    {"id": "typical", "label": "All rot", "input": lambda: {"grid": [r[:] for r in A]}},
    {"id": "edge", "label": "One is cut off", "input": lambda: {"grid": [r[:] for r in B]}},
    {"id": "worst-case", "label": "Nothing fresh", "input": lambda: {"grid": [[0, 2]]}},
]


def bfs_by_minute(grid):
    rows, cols = len(grid), len(grid[0])
    #> Every already-rotten orange starts the clock at the same instant, so BFS
    #> begins from all of them at once rather than from a single source.
    frontier = []
    fresh = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                frontier.append([r, c])
            elif grid[r][c] == 1:
                fresh += 1
    minutes = 0
    while frontier and fresh > 0:
        nxt = []
        for cell in frontier:
            for d in ([1, 0], [-1, 0], [0, 1], [0, -1]):
                nr, nc = cell[0] + d[0], cell[1] + d[1]
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    #> Rot it now so no other neighbour claims it this same minute.
                    grid[nr][nc] = 2
                    fresh -= 1
                    nxt.append([nr, nc])
        #> One whole ring per pass is what makes each pass exactly one minute.
        frontier = nxt
        minutes += 1
    #> Anything still fresh was never reachable from any rotten orange.
    return -1 if fresh > 0 else minutes


def sweep_until_stable(grid):
    #> No queue and no frontier: sweep the whole grid each minute, rotting every
    #> fresh orange next to a rotten one, and stop when a pass changes nothing.
    rows, cols = len(grid), len(grid[0])
    minutes = 0
    while True:
        #> Collect this minute's victims before writing, or a newly rotten
        #> orange would infect its neighbour within the same minute.
        doomed = []
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] != 1:
                    continue
                for d in ([1, 0], [-1, 0], [0, 1], [0, -1]):
                    nr, nc = r + d[0], c + d[1]
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 2:
                        doomed.append([r, c])
        if not doomed:
            #> A pass with no change means everything reachable has rotted.
            break
        for cell in doomed:
            grid[cell[0]][cell[1]] = 2
        minutes += 1
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                #> Something fresh survived, so it was never reachable.
                return -1
    return minutes


APPROACHES = [
    {"id": "sweep", "label": "Sweep until nothing changes", "fn": sweep_until_stable,
     "complexity": {"time": "O(rc \u00b7 minutes)", "space": "O(rc)"},
     "viz": {"grid": "grid", "doomed": "cells:grid", "r": "row:grid", "c": "col:grid"}},
    {"id": "bfs", "label": "BFS from every rotten orange", "fn": bfs_by_minute,
     "complexity": {"time": "O(rc)", "space": "O(rc)"},
     "viz": {"grid": "grid", "frontier": "cells:grid", "nxt": "array", "cell": "array"}},
]
