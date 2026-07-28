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


APPROACHES = [
    {"id": "trie", "label": "Trie with branching search", "fn": wildcard_trie,
     "complexity": {"time": "O(26^dots · n)", "space": "O(total chars)"},
     "viz": {"root": "trie", "node": "trie", "out": "queue", "queries": "array", "$calls": "recursion"}},
]
