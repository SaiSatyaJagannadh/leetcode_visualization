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


APPROACHES = [
    {"id": "bfs", "label": "BFS one letter at a time", "fn": bfs,
     "complexity": {"time": "O(N · L · 26)", "space": "O(N · L)"},
     "viz": {"frontier": "queue", "nxt": "queue", "pool": "map"}},
]
