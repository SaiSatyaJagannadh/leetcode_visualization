META = {
    "slug": "n-queens",
    "title": "N-Queens",
    "pattern": "Backtracking",
    "difficulty": "Hard",
    "leetcode": 51,
    "prompt": "Place n queens on an n by n board so that no two share a row, column or diagonal. Return every distinct arrangement.",
    "examples": [
        {"input": "n = 4", "output": '[[".Q..","...Q","Q...","..Q."],["..Q.","Q...","...Q",".Q.."]]'},
        {"input": "n = 1", "output": '[["Q"]]'},
    ],
    "constraints": ["1 <= n <= 9"],
    "unordered": True,
}

VARIANTS = [
    {"id": "typical", "label": "n = 4", "input": {"n": 4}},
    {"id": "edge", "label": "n = 1", "input": {"n": 1}},
    {"id": "worst-case", "label": "n = 5", "input": {"n": 5}},
]


def backtrack(n, row=0, cols=None, placed=None, out=None):
    if cols is None:
        cols, placed, out = {}, [], []
    if row == n:
        #> A queen in every row without conflict, so record the arrangement.
        out.append(list(placed))
        return out
    for col in range(n):
        #> Placing one queen per row makes row conflicts impossible by
        #> construction, so only columns and diagonals need checking.
        if col in cols:
            continue
        #> Two queens share a diagonal exactly when their row and column
        #> differences match, which is what this scan tests.
        clash = False
        for r in range(row):
            if abs(placed[r] - col) == row - r:
                clash = True
                break
        if clash:
            continue
        cols[col] = True
        placed.append(col)
        backtrack(n, row + 1, cols, placed, out)
        #> Lift the queen back off before trying the next column.
        placed.pop()
        del cols[col]
    return out


APPROACHES = [
    {"id": "backtrack", "label": "One queen per row", "fn": backtrack,
     "complexity": {"time": "O(n!)", "space": "O(n)"},
     "viz": {"placed": "stack", "cols": "map", "out": "queue", "$calls": "recursion"}},
]
