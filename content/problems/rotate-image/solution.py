META = {
    "slug": "rotate-image",
    "title": "Rotate Image",
    "pattern": "Math & Geometry",
    "difficulty": "Medium",
    "leetcode": 48,
    "prompt": "Rotate a square matrix ninety degrees clockwise, modifying it in place rather than building a new one.",
    "examples": [
        {"input": "matrix = [[1,2,3],[4,5,6],[7,8,9]]", "output": "[[7,4,1],[8,5,2],[9,6,3]]"},
        {"input": "matrix = [[1,2],[3,4]]", "output": "[[3,1],[4,2]]"},
    ],
    "constraints": ["1 <= n <= 20", "Must be done in place"],
}

A = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

VARIANTS = [
    {"id": "typical", "label": "3 x 3", "input": lambda: {"matrix": [r[:] for r in A]}},
    {"id": "edge", "label": "Single cell", "input": lambda: {"matrix": [[1]]}},
    {"id": "worst-case", "label": "2 x 2", "input": lambda: {"matrix": [[1, 2], [3, 4]]}},
]


def transpose_then_flip(matrix):
    n = len(matrix)
    #> Step one: reflect across the main diagonal. Rows become columns, which is
    #> a rotation with the wrong handedness.
    for r in range(n):
        for c in range(r + 1, n):
            matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]
    #> Step two: reverse each row. That fixes the handedness, and the two
    #> reflections together are exactly a quarter turn clockwise.
    for r in range(n):
        matrix[r].reverse()
    return matrix


def four_way_cycle(matrix):
    #> Move four cells at a time around the square they form. One temporary
    #> holds the value being displaced, so each element is written exactly once
    #> instead of the two full passes the transpose-and-flip makes.
    n = len(matrix)
    for layer in range(n // 2):
        last = n - 1 - layer
        for i in range(layer, last):
            offset = i - layer
            #> Save the top, then pull each side into the one ahead of it,
            #> travelling anticlockwise so the values land clockwise.
            top = matrix[layer][i]
            matrix[layer][i] = matrix[last - offset][layer]
            matrix[last - offset][layer] = matrix[last][last - offset]
            matrix[last][last - offset] = matrix[i][last]
            matrix[i][last] = top
    return matrix


APPROACHES = [
    {"id": "cycle", "label": "Rotate four cells at a time", "fn": four_way_cycle,
     "complexity": {"time": "O(n\u00b2)", "space": "O(1)"},
     "viz": {"matrix": "grid", "layer": "row:matrix", "i": "col:matrix"}},
    {"id": "transpose-flip", "label": "Transpose, then reverse rows", "fn": transpose_then_flip,
     "complexity": {"time": "O(n²)", "space": "O(1)"},
     "viz": {"matrix": "grid", "r": "row:matrix", "c": "col:matrix"}},
]
