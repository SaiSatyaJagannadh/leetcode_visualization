META = {
    "slug": "walls-and-gates",
    "title": "Walls and Gates",
    "pattern": "Graphs",
    "difficulty": "Medium",
    "leetcode": 286,
    "prompt": "A grid holds gates (0), walls (-1) and empty rooms (a large sentinel). Fill each room with its distance to the nearest gate.",
    "examples": [
        {"input": "one gate at the corner", "output": "distances spread outward from it"},
        {"input": "a room walled off from every gate", "output": "left at the sentinel"},
    ],
    "constraints": ["1 <= rows, cols <= 250", "Movement is four-directional"],
}

INF = 2147483647
A = [[0, INF, INF], [INF, -1, 0]]
SEALED = [[0, -1], [-1, INF]]

VARIANTS = [
    {"id": "typical", "label": "Two gates", "input": lambda: {"grid": [r[:] for r in A]}},
    {"id": "edge", "label": "Room sealed off", "input": lambda: {"grid": [r[:] for r in SEALED]}},
    {"id": "worst-case", "label": "One gate, open floor", "input": lambda: {"grid": [[0, INF], [INF, INF]]}},
]


def bfs_from_all_gates(grid):
    rows, cols = len(grid), len(grid[0])
    #> Starting from every gate at once means the first time BFS reaches a room,
    #> it arrives by the shortest route from the *nearest* gate. Running one BFS
    #> per gate would give the same answer for far more work.
    frontier = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                frontier.append([r, c])
    distance = 0
    while frontier:
        distance += 1
        nxt = []
        for cell in frontier:
            for d in ([1, 0], [-1, 0], [0, 1], [0, -1]):
                nr, nc = cell[0] + d[0], cell[1] + d[1]
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == INF:
                    #> Writing the distance also marks it visited, so no second
                    #> longer route can overwrite it.
                    grid[nr][nc] = distance
                    nxt.append([nr, nc])
        frontier = nxt
    return grid


def one_bfs_per_gate(grid):
    #> The alternative the multi-source version exists to avoid, written out:
    #> run a separate BFS from each gate and keep the smaller distance wherever
    #> two waves overlap. Same answer, one full traversal per gate.
    rows, cols = len(grid), len(grid[0])
    gates = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                gates.append([r, c])
    for gate in gates:
        #> Each gate needs its own visited set, because a cell already reached by
        #> an earlier gate may still be closer to this one.
        seen = {}
        frontier = [gate]
        seen[str(gate[0]) + "," + str(gate[1])] = True
        distance = 0
        while frontier:
            distance += 1
            nxt = []
            for cell in frontier:
                for d in ([1, 0], [-1, 0], [0, 1], [0, -1]):
                    nr, nc = cell[0] + d[0], cell[1] + d[1]
                    if not (0 <= nr < rows and 0 <= nc < cols):
                        continue
                    key = str(nr) + "," + str(nc)
                    if grid[nr][nc] == -1 or key in seen:
                        continue
                    seen[key] = True
                    #> Only improve on what another gate already wrote.
                    if distance < grid[nr][nc]:
                        grid[nr][nc] = distance
                    nxt.append([nr, nc])
            frontier = nxt
    return grid


APPROACHES = [
    {"id": "per-gate", "label": "One BFS per gate", "fn": one_bfs_per_gate,
     "complexity": {"time": "O(gates \u00b7 rc)", "space": "O(rc)"},
     "viz": {"grid": "grid", "frontier": "cells:grid", "seen": "map"}},
    {"id": "multi-bfs", "label": "BFS from every gate at once", "fn": bfs_from_all_gates,
     "complexity": {"time": "O(rc)", "space": "O(rc)"},
     "viz": {"grid": "grid", "frontier": "cells:grid", "nxt": "array"}},
]
