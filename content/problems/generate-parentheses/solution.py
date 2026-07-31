META = {
    "slug": "generate-parentheses",
    "title": "Generate Parentheses",
    "pattern": "Stack",
    "difficulty": "Medium",
    "leetcode": 22,
    "prompt": "Given n pairs of brackets, produce every string of that many pairs in which the brackets are correctly balanced.",
    "examples": [
        {"input": "n = 3", "output": '["((()))","(()())","(())()","()(())","()()()"]'},
        {"input": "n = 1", "output": '["()"]'},
    ],
    "constraints": ["1 <= n <= 8"],
}

VARIANTS = [
    {"id": "typical", "label": "n = 2", "input": {"n": 2}},
    {"id": "edge", "label": "n = 1", "input": {"n": 1}},
    {"id": "worst-case", "label": "n = 3", "input": {"n": 3}},
]


def backtrack(n, current="", opened=0, closed=0, out=None):
    if out is None:
        out = []
    if len(current) == 2 * n:
        #> Used every bracket, and the rules below guaranteed balance the whole way.
        out.append(current)
        return out
    if opened < n:
        #> An opener is legal whenever we haven't spent all n.
        backtrack(n, current + "(", opened + 1, closed, out)
    if closed < opened:
        #> A closer is legal only when something is still open. This one condition
        #> is what stops every invalid string from ever being built.
        backtrack(n, current + ")", opened, closed + 1, out)
    return out


CACHE = {}


def by_decomposition(n):
    #> A structural view instead of an incremental one. Every valid string
    #> starts with "(" whose partner closes somewhere; that split leaves an
    #> inner group and a trailing group, each valid in its own right.
    CACHE.clear()
    return _made(n)


def _made(n):
    if n == 0:
        #> Exactly one arrangement of nothing: the empty string.
        return [""]
    if n in CACHE:
        return CACHE[n]
    out = []
    for i in range(n - 1, -1, -1):
        #> i pairs go inside the first bracket, the remaining n-1-i after it.
        #> Every valid string is produced exactly once by exactly one split.
        #> Counting i downward puts the most deeply nested split first, which is
        #> the order the backtracking version reaches them in — it tries "("
        #> before ")" at every step.
        for inner in _made(i):
            for rest in _made(n - 1 - i):
                out.append("(" + inner + ")" + rest)
    CACHE[n] = out
    return out


APPROACHES = [
    {"id": "decompose", "label": "Split at the matching bracket", "fn": by_decomposition,
     "complexity": {"time": "O(4\u207f / \u221an)", "space": "O(4\u207f / \u221an)"},
     "viz": {"out": "queue", "CACHE": "map", "$calls": "recursion"}},
    {"id": "backtrack", "label": "Backtracking", "fn": backtrack,
     "complexity": {"time": "O(4ⁿ / √n)", "space": "O(n)"},
     "viz": {"out": "queue", "$calls": "recursion"}},
]
