META = {
    "slug": "set-matrix-zeroes",
    "title": "Set Matrix Zeroes",
    "pattern": "Math & Geometry",
    "difficulty": "Medium",
    "leetcode": 73,
    "prompt": "Wherever the matrix holds a zero, blank that cell's whole row and column. Do it in place.",
    "examples": [
        {"input": "matrix = [[1,1,1],[1,0,1],[1,1,1]]", "output": "[[1,0,1],[0,0,0],[1,0,1]]"},
        {"input": "matrix = [[1,2],[3,4]]", "output": "unchanged"},
    ],
    "constraints": ["1 <= rows, cols <= 200"],
}

A = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
B = [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]

VARIANTS = [
    {"id": "typical", "label": "One zero", "input": lambda: {"matrix": [r[:] for r in A]}},
    {"id": "edge", "label": "No zeros", "input": lambda: {"matrix": [[1, 2], [3, 4]]}},
    {"id": "worst-case", "label": "Zeros on the edge", "input": lambda: {"matrix": [r[:] for r in B]}},
]


def mark_then_apply(matrix):
    rows, cols = len(matrix), len(matrix[0])
    #> Blanking as we find zeros would create new zeros and cascade. So record
    #> which rows and columns are doomed first, and only then apply.
    dead_rows = {}
    dead_cols = {}
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == 0:
                dead_rows[r] = True
                dead_cols[c] = True
    for r in range(rows):
        for c in range(cols):
            if r in dead_rows or c in dead_cols:
                matrix[r][c] = 0
    return matrix


def use_the_first_row_and_column(matrix):
    #> No side tables: store the doomed flags inside the matrix itself, in row 0
    #> and column 0. They overlap at [0][0], so one extra flag covers the column.
    rows, cols = len(matrix), len(matrix[0])
    first_col = False
    for r in range(rows):
        if matrix[r][0] == 0:
            first_col = True
        for c in range(1, cols):
            if matrix[r][c] == 0:
                #> Mark the row and column headers rather than blanking now.
                matrix[r][0] = 0
                matrix[0][c] = 0
    #> Apply inwards-out, so the headers survive until everything has read them.
    for r in range(rows - 1, -1, -1):
        for c in range(cols - 1, 0, -1):
            if matrix[r][0] == 0 or matrix[0][c] == 0:
                matrix[r][c] = 0
        if first_col:
            matrix[r][0] = 0
    return matrix


APPROACHES = [
    {"id": "in-place", "label": "Store the flags in the matrix", "fn": use_the_first_row_and_column,
     "complexity": {"time": "O(rc)", "space": "O(1)"},
     "viz": {"matrix": "grid", "r": "row:matrix", "c": "col:matrix"}},
    {"id": "mark", "label": "Record first, blank second", "fn": mark_then_apply,
     "complexity": {"time": "O(rc)", "space": "O(r + c)"},
     "viz": {"matrix": "grid", "r": "row:matrix", "c": "col:matrix", "dead_rows": "map", "dead_cols": "map"}},
]
