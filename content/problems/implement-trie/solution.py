META = {
    "slug": "implement-trie",
    "title": "Implement Trie",
    "pattern": "Tries",
    "difficulty": "Medium",
    "leetcode": 208,
    "prompt": (
        "Build a prefix tree supporting insert, exact-word lookup, and prefix "
        "lookup. The trace below inserts a batch of words, then runs the queries."
    ),
    "examples": [
        {"input": 'insert("apple"), search("apple")', "output": "true"},
        {"input": 'search("app")', "output": "false",
         "why": '"app" is a prefix of an inserted word but was never inserted itself.'},
        {"input": 'startsWith("app")', "output": "true",
         "why": "Prefix lookup only needs the path to exist, not to end a word."},
    ],
    "constraints": ["1 <= word length <= 2000", "Words are lowercase English letters"],
}

VARIANTS = [
    {
        "id": "typical",
        "label": "Shared prefixes",
        "input": {"words": ["apple", "app"], "queries": ["apple", "app", "ap"]},
    },
    {"id": "edge", "label": "One word", "input": {"words": ["a"], "queries": ["a", "ab"]}},
    {
        "id": "worst-case",
        "label": "Branching",
        "input": {"words": ["car", "cat", "cart"], "queries": ["car", "ca", "cart"]},
    },
]

END = "$"


def trie(words, queries):
    root = {}
    for word in words:
        node = root
        for ch in word:
            #> Walk down if this letter already branches here, otherwise create it.
            #> Shared prefixes cost nothing extra — that is the point of a trie.
            if ch not in node:
                node[ch] = {}
            node = node[ch]
        #> Mark where a real word ends. Without this, "app" inside "apple" would
        #> look like an inserted word when it never was.
        node[END] = {}

    found = []
    for query in queries:
        node = root
        ok = True
        for ch in query:
            if ch not in node:
                #> The path dies here, so no inserted word starts with this.
                ok = False
                break
            node = node[ch]
        #> Reaching the end of the path is not enough; it has to be a marked word.
        found.append(ok and END in node)
    return found


def sorted_list(words, queries):
    #> No trie: keep the words sorted and binary-search each query. Lookups are
    #> log n rather than length-of-word, and the prefix sharing that makes a trie
    #> cheap on memory is entirely absent — every word is stored in full.
    stored = sorted(words)
    out = []
    for q in queries:
        lo, hi = 0, len(stored) - 1
        found = False
        while lo <= hi:
            mid = (lo + hi) // 2
            if stored[mid] == q:
                #> Exact hit. Note this answers "was this word inserted", which
                #> is the same question the trie's end-marker answers.
                found = True
                break
            if stored[mid] < q:
                lo = mid + 1
            else:
                hi = mid - 1
        out.append(found)
    return out


APPROACHES = [
    {"id": "sorted-list", "label": "Sorted list and binary search", "fn": sorted_list,
     "complexity": {"time": "O(q log w)", "space": "O(total chars)"},
     "viz": {"stored": "array", "out": "queue", "lo": "pointer:stored", "hi": "pointer:stored", "mid": "pointer:stored"}},
    {
        "id": "nested-dict",
        "label": "Nested dictionaries",
        "fn": trie,
        "complexity": {"time": "O(total chars)", "space": "O(total chars)"},
        "viz": {"root": "trie", "node": "trie", "words": "array", "queries": "array", "found": "queue"},
    }
]
