META = {
    "slug": "alien-dictionary",
    "title": "Alien Dictionary",
    "pattern": "Advanced Graphs",
    "difficulty": "Hard",
    "leetcode": 269,
    "prompt": "A list of words is sorted according to an unknown alphabet. Work out an ordering of the letters consistent with that sorting, or return empty if the list contradicts itself.",
    "examples": [
        {"input": 'words = ["wrt","wrf","er","ett","rftt"]', "output": '"wertf"'},
        {"input": 'words = ["z","x","z"]', "output": '""', "why": "z before x and x before z is impossible."},
    ],
    "constraints": ["1 <= len(words) <= 100", "Lowercase letters only"],
}

VARIANTS = [
    {"id": "typical", "label": "Solvable", "input": {"words": ["wrt", "wrf", "er", "ett", "rftt"]}},
    {"id": "edge", "label": "Contradiction", "input": {"words": ["z", "x", "z"]}},
    {"id": "worst-case", "label": "Two letters", "input": {"words": ["ab", "aa"]}},
]


def topological(words):
    after = {}
    for w in words:
        for ch in w:
            after.setdefault(ch, {})
    for i in range(len(words) - 1):
        a, b = words[i], words[i + 1]
        #> Adjacent words reveal exactly one fact: at their first differing
        #> letter, a's letter comes before b's. Everything after that is unknown.
        found = False
        for j in range(min(len(a), len(b))):
            if a[j] != b[j]:
                after[a[j]][b[j]] = True
                found = True
                break
        if not found and len(a) > len(b):
            #> A word can't come before its own prefix, so this list is invalid.
            return ""

    #> Now it's an ordinary topological sort over the letters.
    state = {ch: "new" for ch in after}
    order = []
    for ch in after:
        if not _visit(ch, after, state, order):
            return ""
    order.reverse()
    return "".join(order)


def _visit(ch, after, state, order):
    if state[ch] == "doing":
        return False  #> Back on a letter we're mid-way through: a cycle.
    if state[ch] == "done":
        return True
    state[ch] = "doing"
    for nxt in after[ch]:
        if not _visit(nxt, after, state, order):
            return False
    state[ch] = "done"
    #> Appended after its dependants, so reversing at the end gives the order.
    order.append(ch)
    return True


APPROACHES = [
    {"id": "topo", "label": "Order from adjacent pairs", "fn": topological,
     "complexity": {"time": "O(total chars)", "space": "O(1)"},
     "viz": {"words": "array", "after": "map", "order": "stack", "$calls": "recursion"}},
]
