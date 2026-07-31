META = {
    "slug": "number-of-islands",
    "title": "Number of Islands",
    "pattern": "Graphs",
    "difficulty": "Medium",
    "leetcode": 200,
    "prompt": (
        "A grid holds 1 for land and 0 for water. An island is a group of 1s "
        "joined edge to edge, horizontally or vertically. Count the islands."
    ),
    "examples": [
        {"input": "grid = [[1,1,0,0],[1,1,0,0],[0,0,1,0],[0,0,0,1]]", "output": "3",
         "why": "The 2x2 block, the single cell, and the corner cell are separate."},
        {"input": "grid = [[0,0],[0,0]]", "output": "0", "why": "All water."},
    ],
    "constraints": ["1 <= rows, cols <= 300", "Each cell is 0 or 1"],
}

TYPICAL = [[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
SNAKE = [[1, 1, 1], [0, 0, 1], [1, 1, 1]]

VARIANTS = [
    {"id": "typical", "label": "Three islands", "input": lambda: {"grid": [r[:] for r in TYPICAL]}},
    {"id": "edge", "label": "All water", "input": lambda: {"grid": [[0, 0], [0, 0]]}},
    {"id": "worst-case", "label": "One winding island", "input": lambda: {"grid": [r[:] for r in SNAKE]}},
]


def flood(grid):
    rows, cols = len(grid), len(grid[0])
    count = 0
    for r in range(rows):
        for c in range(cols):
            #> Only unvisited land starts a new island; everything else is already counted.
            if grid[r][c] != 1:
                continue
            count += 1
            #> Sink this whole island so its other cells never start a second count.
            stack = [[r, c]]
            while stack:
                cell = stack.pop()
                cr, cc = cell[0], cell[1]
                if cr < 0 or cr >= rows or cc < 0 or cc >= cols or grid[cr][cc] != 1:
                    continue  #> Off the grid or not land — nothing to sink here.
                grid[cr][cc] = 2  #> Mark as visited by turning it into a third value.
                #> Push all four neighbours; the guard above filters them.
                stack.append([cr + 1, cc])
                stack.append([cr - 1, cc])
                stack.append([cr, cc + 1])
                stack.append([cr, cc - 1])
    return count


def bfs_queue(grid):
    rows, cols = len(grid), len(grid[0])
    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 1:
                continue
            count += 1
            #> A queue instead of a stack. Same cells get sunk, but they are
            #> reached in rings spreading outward rather than one long tendril
            #> at a time — watch the highlighted cells to see the difference.
            queue = [[r, c]]
            grid[r][c] = 2
            while queue:
                cell = queue.pop(0)
                cr, cc = cell[0], cell[1]
                #> Mark on the way IN, not on the way out. With a queue a cell
                #> can be enqueued twice before it is ever popped.
                for step in [[1, 0], [-1, 0], [0, 1], [0, -1]]:
                    nr = cr + step[0]
                    nc = cc + step[1]
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                        grid[nr][nc] = 2
                        queue.append([nr, nc])
    return count


APPROACHES = [
    {"id": "bfs", "label": "Flood fill with a queue", "fn": bfs_queue,
     "complexity": {"time": "O(rc)", "space": "O(rc)"},
     "viz": {"grid": "grid", "r": "row:grid", "c": "col:grid", "queue": "cells:grid", "cell": "array"}},
    {
        "id": "flood",
        "label": "Flood fill",
        "fn": flood,
        "complexity": {"time": "O(rc)", "space": "O(rc)"},
        "viz": {"grid": "grid", "r": "row:grid", "c": "col:grid", "stack": "cells:grid", "cell": "array"},
    }
]
