META = {
    "slug": "word-ladder",
    "title": "Word Ladder",
    "pattern": "Graphs",
    "difficulty": "Hard",
    "leetcode": 127,
    "prompt": "Change one letter at a time, with every intermediate word in the given list, to get from the start word to the end word. Return the number of words in the shortest such chain, or 0 if none exists.",
    "examples": [
        {"input": 'begin = "hit", end = "cog", words = ["hot","dot","dog","lot","log","cog"]', "output": "5",
         "why": "hit → hot → dot → dog → cog."},
        {"input": 'end = "cog" missing from the list', "output": "0"},
    ],
    "constraints": ["1 <= word length <= 10", "All words are the same length"],
}

WORDS = ["hot", "dot", "dog", "cog"]

VARIANTS = [
    {"id": "typical", "label": "Chain exists", "input": {"begin": "hit", "end": "cog", "words": list(WORDS)}},
    {"id": "edge", "label": "End word missing", "input": {"begin": "hit", "end": "cog", "words": ["hot", "dot", "dog"]}},
    {"id": "worst-case", "label": "One step", "input": {"begin": "hit", "end": "hot", "words": ["hot"]}},
]


def bfs(begin, end, words):
    pool = {}
    for w in words:
        pool[w] = True
    if end not in pool:
        #> The target isn't a legal word, so no chain can possibly finish.
        return 0
    #> BFS, not DFS: the first time we reach `end`, we reached it by the fewest
    #> steps. A depth-first walk would find *a* chain, not the shortest.
    #> Only letters that actually occur in the list are worth trying; the other
    #> twenty-odd can never produce a word that's in the pool.
    letters = {}
    for w in words:
        for ch in w:
            letters[ch] = True
    frontier = [begin]
    length = 1
    while frontier:
        nxt = []
        for word in frontier:
            if word == end:
                return length
            for i in range(len(word)):
                for ch in letters:
                    candidate = word[:i] + ch + word[i + 1:]
                    if candidate in pool:
                        #> Remove it from the pool the moment it's queued, so no
                        #> other branch re-explores it on a longer route.
                        del pool[candidate]
                        nxt.append(candidate)
        frontier = nxt
        length += 1
    return 0


def compare_every_pair(begin, end, words):
    #> Instead of mutating letters to find neighbours, ask directly which words
    #> differ by exactly one character. That costs a scan of the whole list per
    #> step, where the letter-substitution version costs only the word's length.
    pool = [w for w in words]
    if end not in pool:
        return 0
    frontier = [begin]
    used = {begin: True}
    length = 1
    while frontier:
        length += 1
        nxt = []
        for word in frontier:
            for other in pool:
                #> A neighbour is any unused word one substitution away.
                if other not in used and _one_apart(word, other):
                    if other == end:
                        return length
                    used[other] = True
                    nxt.append(other)
        frontier = nxt
    return 0


def _one_apart(a, b):
    if len(a) != len(b):
        return False
    diff = 0
    for i in range(len(a)):
        if a[i] != b[i]:
            diff += 1
    #> Exactly one mismatch: zero means the same word, two or more is too far.
    return diff == 1


APPROACHES = [
    {"id": "pairwise", "label": "Compare every pair of words", "fn": compare_every_pair,
     "complexity": {"time": "O(n\u00b2 \u00b7 L)", "space": "O(n)"},
     "viz": {"pool": "array", "frontier": "queue", "used": "map"}},
    {"id": "bfs", "label": "BFS one letter at a time", "fn": bfs,
     "complexity": {"time": "O(N · L · 26)", "space": "O(N · L)"},
     "viz": {"frontier": "queue", "nxt": "queue", "pool": "map"}},
]
