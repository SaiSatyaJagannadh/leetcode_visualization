META = {
    "slug": "max-area-of-island",
    "title": "Max Area of Island",
    "pattern": "Graphs",
    "difficulty": "Medium",
    "leetcode": 695,
    "prompt": "In a grid of land and water, find the number of cells in the largest connected patch of land. Return 0 if there is none.",
    "examples": [
        {"input": "grid = [[1,1,0],[1,0,0],[0,0,1]]", "output": "3"},
        {"input": "grid = [[0,0],[0,0]]", "output": "0"},
    ],
    "constraints": ["1 <= rows, cols <= 50", "Each cell is 0 or 1"],
}

A = [[1, 1, 0, 0], [1, 0, 0, 1], [0, 0, 1, 1]]

VARIANTS = [
    {"id": "typical", "label": "Two islands", "input": lambda: {"grid": [r[:] for r in A]}},
    {"id": "edge", "label": "All water", "input": lambda: {"grid": [[0, 0], [0, 0]]}},
    {"id": "worst-case", "label": "One big island", "input": lambda: {"grid": [[1, 1], [1, 1]]}},
]


def flood(grid):
    best = 0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] != 1:
                continue
            #> Sink the whole patch while counting it, so no cell is ever counted
            #> twice and no later scan restarts inside the same island.
            area = 0
            stack = [[r, c]]
            while stack:
                cell = stack.pop()
                cr, cc = cell[0], cell[1]
                if cr < 0 or cr >= len(grid) or cc < 0 or cc >= len(grid[0]):
                    continue
                if grid[cr][cc] != 1:
                    continue
                grid[cr][cc] = 2
                area += 1
                stack.append([cr + 1, cc])
                stack.append([cr - 1, cc])
                stack.append([cr, cc + 1])
                stack.append([cr, cc - 1])
            if area > best:
                best = area
    return best


def recursive_area(grid):
    #> Recursion instead of an explicit stack. The call tree is the search: each
    #> frame sinks its own cell and asks its four neighbours for their areas,
    #> so the total comes back up the tree rather than being accumulated in a loop.
    best = 0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] != 1:
                continue
            area = _sink(grid, r, c)
            if area > best:
                best = area
    return best


def _sink(grid, r, c):
    if r < 0 or r >= len(grid) or c < 0 or c >= len(grid[0]):
        return 0
    if grid[r][c] != 1:
        #> Water, or land already counted on this same island.
        return 0
    #> Mark before recursing, or the neighbour recurses straight back here.
    grid[r][c] = 2
    return 1 + _sink(grid, r + 1, c) + _sink(grid, r - 1, c) + _sink(grid, r, c + 1) + _sink(grid, r, c - 1)


APPROACHES = [
    {"id": "recursive", "label": "Recursive flood fill", "fn": recursive_area,
     "complexity": {"time": "O(rc)", "space": "O(rc)"},
     "viz": {"grid": "grid", "r": "row:grid", "c": "col:grid", "$calls": "recursion"}},
    {"id": "flood", "label": "Flood fill, measuring", "fn": flood,
     "complexity": {"time": "O(rc)", "space": "O(rc)"},
     "viz": {"grid": "grid", "stack": "cells:grid", "r": "row:grid", "c": "col:grid"}},
]
