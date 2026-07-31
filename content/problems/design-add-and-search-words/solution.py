META = {
    "slug": "design-add-and-search-words",
    "title": "Design Add and Search Words",
    "pattern": "Tries",
    "difficulty": "Medium",
    "leetcode": 211,
    "prompt": "Store words and search them, where a search string may contain '.' as a wildcard matching any single letter.",
    "examples": [
        {"input": 'add("bad"), add("dad"), search("pad")', "output": "false"},
        {"input": 'search(".ad")', "output": "true", "why": "The dot matches b or d."},
        {"input": 'search("b..")', "output": "true"},
    ],
    "constraints": ["1 <= word length <= 25", "Search strings may contain dots"],
}

VARIANTS = [
    {"id": "typical", "label": "Wildcards", "input": {"words": ["bad", "dad", "mad"], "queries": ["pad", ".ad", "b.."]}},
    {"id": "edge", "label": "No wildcard", "input": {"words": ["a"], "queries": ["a", "b"]}},
    {"id": "worst-case", "label": "All wildcards", "input": {"words": ["abc", "abd"], "queries": ["...", "ab."]}},
]

END = "$"


def wildcard_trie(words, queries):
    root = {}
    for word in words:
        node = root
        for ch in word:
            if ch not in node:
                node[ch] = {}
            node = node[ch]
        node[END] = {}

    out = []
    for query in queries:
        #> A dot forces us to try every branch, so the search becomes a small
        #> recursive walk instead of a straight descent.
        out.append(_match(root, query, 0))
    return out


def _match(node, query, i):
    if i == len(query):
        #> Ran out of query. It's a hit only if a word actually ends here.
        return END in node
    ch = query[i]
    if ch == ".":
        for key in node:
            #> Try each real letter. The end marker isn't a letter, so skip it.
            if key != END and _match(node[key], query, i + 1):
                return True
        return False
    if ch not in node:
        return False  #> This path doesn't exist, so nothing below can match.
    return _match(node[ch], query, i + 1)


def scan_every_word(words, queries):
    #> No trie at all: keep the words in a list and compare each query against
    #> every one of them. This is what the trie buys you — the trie shares
    #> prefixes so a query stops as soon as no word can still match.
    out = []
    for query in queries:
        hit = False
        for word in words:
            if _same(word, query):
                hit = True
        out.append(hit)
    return out


def _same(word, query):
    if len(word) != len(query):
        #> A dot matches one character, never zero or several, so length is
        #> a cheap first filter.
        return False
    for i in range(len(query)):
        #> A dot accepts whatever is there; anything else must match exactly.
        if query[i] != "." and query[i] != word[i]:
            return False
    return True


APPROACHES = [
    {"id": "linear-scan", "label": "Compare against every word", "fn": scan_every_word,
     "complexity": {"time": "O(words \u00b7 len)", "space": "O(1)"},
     "viz": {"words": "array", "queries": "array", "out": "queue"}},
    {"id": "trie", "label": "Trie with branching search", "fn": wildcard_trie,
     "complexity": {"time": "O(26^dots · n)", "space": "O(total chars)"},
     "viz": {"root": "trie", "node": "trie", "out": "queue", "queries": "array", "$calls": "recursion"}},
]
