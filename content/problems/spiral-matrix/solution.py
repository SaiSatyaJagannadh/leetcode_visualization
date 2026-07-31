META = {
    "slug": "spiral-matrix",
    "title": "Spiral Matrix",
    "pattern": "Math & Geometry",
    "difficulty": "Medium",
    "leetcode": 54,
    "prompt": (
        "Return all elements of a matrix in spiral order: across the top row, "
        "down the right side, back along the bottom, up the left, then inward."
    ),
    "examples": [
        {"input": "matrix = [[1,2,3],[4,5,6],[7,8,9]]", "output": "[1,2,3,6,9,8,7,4,5]"},
        {"input": "matrix = [[1,2,3]]", "output": "[1,2,3]",
         "why": "A single row never turns a corner."},
    ],
    "constraints": ["1 <= rows, cols <= 10", "-100 <= value <= 100"],
}

SQUARE = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
WIDE = [[1, 2, 3, 4], [5, 6, 7, 8]]

VARIANTS = [
    {"id": "typical", "label": "3 x 3", "input": lambda: {"matrix": [r[:] for r in SQUARE]}},
    {"id": "edge", "label": "Single row", "input": lambda: {"matrix": [[1, 2, 3]]}},
    {"id": "worst-case", "label": "Wide", "input": lambda: {"matrix": [r[:] for r in WIDE]}},
]


def boundaries(matrix):
    out = []
    #> Four walls closing inward. The spiral is just these four shrinking.
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            out.append(matrix[top][c])  #> Across the top row, left to right.
        top += 1  #> That row is spent, so the ceiling drops.
        for r in range(top, bottom + 1):
            out.append(matrix[r][right])  #> Down the right-hand column.
        right -= 1
        #> These two guards matter: after the walls close, a lone row or column
        #> would otherwise be read a second time, backwards.
        if top <= bottom:
            for c in range(right, left - 1, -1):
                out.append(matrix[bottom][c])  #> Back along the bottom, right to left.
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                out.append(matrix[r][left])  #> Up the left-hand column, closing the ring.
            left += 1
    return out


def peel_and_rotate(matrix):
    #> A different mental model: take the whole top row, then rotate what is left
    #> anticlockwise and do it again. Every ring becomes a top row eventually, so
    #> the four-direction bookkeeping disappears entirely.
    rows = [r[:] for r in matrix]
    out = []
    while rows:
        #> The top row is always next in the spiral, by construction.
        top = rows[0]
        for v in top:
            out.append(v)
        rest = rows[1:]
        if not rest:
            break
        #> Rotate the remainder anticlockwise: last column becomes the new top row.
        turned = []
        for c in range(len(rest[0]) - 1, -1, -1):
            row = []
            for r in range(len(rest)):
                row.append(rest[r][c])
            turned.append(row)
        rows = turned
    return out


APPROACHES = [
    {"id": "peel", "label": "Peel the top, rotate the rest", "fn": peel_and_rotate,
     "complexity": {"time": "O(rc)", "space": "O(rc)"},
     "viz": {"matrix": "grid", "rows": "grid", "out": "queue"}},
    {
        "id": "boundaries",
        "label": "Shrinking walls",
        "fn": boundaries,
        "complexity": {"time": "O(mn)", "space": "O(1)"},
        "viz": {"matrix": "grid", "out": "queue"},
    }
]
