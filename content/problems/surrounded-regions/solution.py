META = {
    "slug": "surrounded-regions",
    "title": "Surrounded Regions",
    "pattern": "Graphs",
    "difficulty": "Medium",
    "leetcode": 130,
    "prompt": "In a board of X and O, flip every O that is completely surrounded by X. An O connected to the border is never surrounded, so it survives.",
    "examples": [
        {"input": 'board = [["X","X","X"],["X","O","X"],["X","X","X"]]', "output": "The middle O becomes X"},
        {"input": 'board = [["O"]]', "output": "unchanged", "why": "It touches the border."},
    ],
    "constraints": ["1 <= rows, cols <= 200"],
}

A = [["X", "X", "X", "X"], ["X", "O", "O", "X"], ["X", "X", "O", "X"], ["X", "O", "X", "X"]]

VARIANTS = [
    {"id": "typical", "label": "Some survive", "input": lambda: {"board": [r[:] for r in A]}},
    {"id": "edge", "label": "Single border cell", "input": lambda: {"board": [["O"]]}},
    {"id": "worst-case", "label": "All captured", "input": lambda: {"board": [["X", "X"], ["X", "O"]]}},
]


def from_the_border(board):
    rows, cols = len(board), len(board[0])
    #> Rather than asking "is this region enclosed?", flip the question: mark
    #> everything reachable from the border as safe. Whatever is left is captured.
    for r in range(rows):
        for c in range(cols):
            on_border = r == 0 or c == 0 or r == rows - 1 or c == cols - 1
            if on_border and board[r][c] == "O":
                _mark(board, r, c)
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == "O":
                board[r][c] = "X"  #> Never reached from the border, so captured.
            elif board[r][c] == "S":
                board[r][c] = "O"  #> Safe after all; restore it.
    return board


def _mark(board, r, c):
    stack = [[r, c]]
    while stack:
        cell = stack.pop()
        cr, cc = cell[0], cell[1]
        if cr < 0 or cr >= len(board) or cc < 0 or cc >= len(board[0]):
            continue
        if board[cr][cc] != "O":
            continue
        board[cr][cc] = "S"
        stack.append([cr + 1, cc])
        stack.append([cr - 1, cc])
        stack.append([cr, cc + 1])
        stack.append([cr, cc - 1])


def enclosed_check(board):
    #> The direct reading: for each region, walk it and ask whether it ever
    #> touches the border. Every region gets its own traversal, and a region
    #> that IS safe still has to be walked in full before we know.
    rows, cols = len(board), len(board[0])
    for r in range(rows):
        for c in range(cols):
            if board[r][c] != "O":
                continue
            region = []
            touches = _collect(board, r, c, region)
            for cell in region:
                #> Mark the whole region at once, now that its fate is known.
                board[cell[0]][cell[1]] = "O" if touches else "X"
    return board


def _collect(board, r, c, region):
    rows, cols = len(board), len(board[0])
    stack = [[r, c]]
    touches = False
    while stack:
        cell = stack.pop()
        cr, cc = cell[0], cell[1]
        if not (0 <= cr < rows and 0 <= cc < cols) or board[cr][cc] != "O":
            continue
        #> A third value keeps this region from being re-collected later.
        board[cr][cc] = "V"
        region.append([cr, cc])
        if cr == 0 or cc == 0 or cr == rows - 1 or cc == cols - 1:
            #> Reaches the edge, so the whole region survives.
            touches = True
        stack.append([cr + 1, cc])
        stack.append([cr - 1, cc])
        stack.append([cr, cc + 1])
        stack.append([cr, cc - 1])
    return touches


APPROACHES = [
    {"id": "per-region", "label": "Walk each region, ask if it escapes", "fn": enclosed_check,
     "complexity": {"time": "O(rc)", "space": "O(rc)"},
     "viz": {"board": "grid", "region": "cells:board", "stack": "cells:board"}},
    {"id": "border", "label": "Mark from the border inward", "fn": from_the_border,
     "complexity": {"time": "O(rc)", "space": "O(rc)"},
     "viz": {"board": "grid", "r": "row:board", "c": "col:board"}},
]
