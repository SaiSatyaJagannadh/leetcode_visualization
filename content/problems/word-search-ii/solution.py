META = {
    "slug": "word-search-ii",
    "title": "Word Search II",
    "pattern": "Tries",
    "difficulty": "Hard",
    "leetcode": 212,
    "prompt": "Given a grid of letters and a word list, return every word that can be spelled by walking to adjacent cells without reusing a cell.",
    "examples": [
        {"input": 'board = [["o","a"],["e","t"]], words = ["oat","oe","xyz"]', "output": '["oat","oe"]'},
        {"input": 'board = [["a"]], words = ["a"]', "output": '["a"]'},
    ],
    "constraints": ["1 <= rows, cols <= 12", "1 <= len(words) <= 3 * 10^4"],
}

BOARD = [["o", "a", "t"], ["e", "t", "s"]]

VARIANTS = [
    {"id": "typical", "label": "Two hits", "input": lambda: {"board": [r[:] for r in BOARD], "words": ["oat", "oe", "xyz"]}},
    {"id": "edge", "label": "Single cell", "input": lambda: {"board": [["a"]], "words": ["a", "ab"]}},
    {"id": "worst-case", "label": "Shared prefixes", "input": lambda: {"board": [r[:] for r in BOARD], "words": ["oa", "oat", "oats"]}},
]

END = "$"


def trie_walk(board, words):
    #> Building a trie of the word list means one pass over the board can hunt for
    #> every word at once, and a dead prefix kills all of them together.
    root = {}
    for word in words:
        node = root
        for ch in word:
            if ch not in node:
                node[ch] = {}
            node = node[ch]
        node[END] = word

    found = []
    for r in range(len(board)):
        for c in range(len(board[0])):
            _hunt(board, r, c, root, found)
    return sorted(found)


def _hunt(board, r, c, node, found):
    if r < 0 or r >= len(board) or c < 0 or c >= len(board[0]):
        return
    ch = board[r][c]
    if ch not in node:
        #> No word in the whole list continues this way, so stop immediately.
        return
    nxt = node[ch]
    if END in nxt:
        #> A complete word ends here. Record it and clear the marker so a second
        #> route to the same word doesn't report it twice.
        found.append(nxt[END])
        del nxt[END]
    #> Mark the cell as used for this path only, then restore it on the way out.
    board[r][c] = "#"
    _hunt(board, r + 1, c, nxt, found)
    _hunt(board, r - 1, c, nxt, found)
    _hunt(board, r, c + 1, nxt, found)
    _hunt(board, r, c - 1, nxt, found)
    board[r][c] = ch


APPROACHES = [
    {"id": "trie", "label": "Trie-guided backtracking", "fn": trie_walk,
     "complexity": {"time": "O(rc · 4^L)", "space": "O(total chars)"},
     "viz": {"board": "grid", "root": "trie", "found": "queue", "$calls": "recursion"}},
]
