META = {
    "slug": "search-a-2d-matrix",
    "title": "Search a 2D Matrix",
    "pattern": "Binary Search",
    "difficulty": "Medium",
    "leetcode": 74,
    "prompt": "Each row of the matrix is sorted, and every value in a row is smaller than every value in the row below. Decide whether a target appears, in logarithmic time.",
    "examples": [
        {"input": "matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 3", "output": "true"},
        {"input": "same matrix, target = 13", "output": "false"},
    ],
    "constraints": ["1 <= rows, cols <= 100", "The matrix reads as one sorted sequence"],
}

M = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]

VARIANTS = [
    {"id": "typical", "label": "Found", "input": lambda: {"matrix": [r[:] for r in M], "target": 16}},
    {"id": "edge", "label": "Missing", "input": lambda: {"matrix": [r[:] for r in M], "target": 13}},
    {"id": "worst-case", "label": "Last cell", "input": lambda: {"matrix": [r[:] for r in M], "target": 60}},
]


def row_then_column(matrix, target):
    #> Find the row whose range could contain the target, then search inside it.
    row = 0
    while row < len(matrix) and matrix[row][-1] < target:
        row += 1  #> This row tops out below the target, so skip the whole thing.
    if row == len(matrix):
        return False
    lo, hi = 0, len(matrix[row]) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if matrix[row][mid] == target:
            return True
        if matrix[row][mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False


def flat_binary(matrix, target):
    rows, cols = len(matrix), len(matrix[0])
    #> The ordering guarantee means the grid *is* one sorted array, folded. So
    #> search index 0..rows*cols-1 and unfold each guess back into (row, col).
    lo, hi = 0, rows * cols - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        value = matrix[mid // cols][mid % cols]
        if value == target:
            return True
        if value < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return False


APPROACHES = [
    {"id": "row-then-column", "label": "Find row, then search it", "fn": row_then_column,
     "complexity": {"time": "O(m + log n)", "space": "O(1)"},
     "viz": {"matrix": "grid", "row": "row:matrix", "mid": "col:matrix"}},
    {"id": "flat", "label": "Treat it as one array", "fn": flat_binary,
     "complexity": {"time": "O(log mn)", "space": "O(1)"},
     "viz": {"matrix": "grid"}},
]
