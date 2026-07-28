META = {
    "slug": "word-search",
    "title": "Word Search",
    "pattern": "Backtracking",
    "difficulty": "Medium",
    "leetcode": 79,
    "prompt": "Decide whether a word can be spelled by walking between horizontally or vertically adjacent cells of a letter grid, without reusing a cell.",
    "examples": [
        {"input": 'board = [["A","B"],["S","F"]], word = "ABF"', "output": "true"},
        {"input": 'word = "ABFS"', "output": "false", "why": "S is not adjacent to F along that route."},
    ],
    "constraints": ["1 <= rows, cols <= 6", "1 <= len(word) <= 15"],
}

BOARD = [["A", "B", "C"], ["S", "F", "D"], ["A", "D", "E"]]

VARIANTS = [
    {"id": "typical", "label": "Found", "input": lambda: {"board": [r[:] for r in BOARD], "word": "ABCD"}},
    {"id": "edge", "label": "Not found", "input": lambda: {"board": [r[:] for r in BOARD], "word": "ABFZ"}},
    {"id": "worst-case", "label": "Needs backtracking", "input": lambda: {"board": [r[:] for r in BOARD], "word": "ABCDE"}},
]


def search(board, word):
    for r in range(len(board)):
        for c in range(len(board[0])):
            #> Any cell could start the word, so try them all.
            if _walk(board, r, c, word, 0):
                return True
    return False


def _walk(board, r, c, word, i):
    if i == len(word):
        #> Every letter placed, so the path spelled the word.
        return True
    if r < 0 or r >= len(board) or c < 0 or c >= len(board[0]):
        return False
    if board[r][c] != word[i]:
        #> Wrong letter here, so this route is dead.
        return False
    #> Blank the cell so the rest of this path can't step back onto it. The
    #> board itself is the visited-set, which is why it must be restored below.
    saved = board[r][c]
    board[r][c] = "#"
    found = (
        _walk(board, r + 1, c, word, i + 1)
        or _walk(board, r - 1, c, word, i + 1)
        or _walk(board, r, c + 1, word, i + 1)
        or _walk(board, r, c - 1, word, i + 1)
    )
    #> Undo, so a different path is free to use this cell.
    board[r][c] = saved
    return found


APPROACHES = [
    {"id": "backtrack", "label": "Backtracking on the grid", "fn": search,
     "complexity": {"time": "O(rc · 4^L)", "space": "O(L)"},
     "viz": {"board": "grid", "$calls": "recursion"}},
]
