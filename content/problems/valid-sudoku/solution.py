META = {
    "slug": "valid-sudoku",
    "title": "Valid Sudoku",
    "pattern": "Arrays & Hashing",
    "difficulty": "Medium",
    "leetcode": 36,
    "prompt": "Decide whether a partly filled 9x9 board breaks any Sudoku rule. Only the filled cells are checked, and the board need not be solvable.",
    "examples": [
        {"input": "a board with no repeats in any row, column or box", "output": "true"},
        {"input": "two 8s in the same 3x3 box", "output": "false"},
    ],
    "constraints": ["The board is always 9x9", "Cells hold a digit or a dot"],
}


def board(rows):
    return [list(r) for r in rows]


GOOD = ["53..7....", "6..195...", ".98....6.", "8...6...3", "4..8.3..1",
        "7...2...6", ".6....28.", "...419..5", "....8..79"]
BAD = ["8" + GOOD[0][1:]] + GOOD[1:2] + ["8" + GOOD[2][1:]] + GOOD[3:]

VARIANTS = [
    {"id": "typical", "label": "Valid", "input": lambda: {"grid": board(GOOD)}},
    {"id": "edge", "label": "Repeat in a column", "input": lambda: {"grid": board(BAD)}},
    {"id": "worst-case", "label": "Empty board", "input": lambda: {"grid": board(["........."] * 9)}},
]


def three_sets(grid):
    #> One tally per row, per column, and per 3x3 box. Checking all three as we
    #> go means a single pass over the board settles every rule at once.
    rows = {}
    cols = {}
    boxes = {}
    for r in range(9):
        for c in range(9):
            ch = grid[r][c]
            if ch == ".":
                continue
            #> Integer division turns a coordinate into its box number, which is
            #> what lets boxes be checked with the same machinery as rows.
            box = (r // 3) * 3 + (c // 3)
            rkey, ckey, bkey = "r" + str(r) + ch, "c" + str(c) + ch, "b" + str(box) + ch
            if rkey in rows or ckey in cols or bkey in boxes:
                return False
            rows[rkey] = True
            cols[ckey] = True
            boxes[bkey] = True
    return True


APPROACHES = [
    {"id": "three-sets", "label": "Row, column and box tallies", "fn": three_sets,
     "complexity": {"time": "O(1)", "space": "O(1)"},
     "viz": {"grid": "grid", "r": "row:grid", "c": "col:grid"}},
]
