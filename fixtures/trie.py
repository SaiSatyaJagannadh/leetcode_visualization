"""A trie is a nested dict, so it needs no node objects and no baked layout —
the renderer walks it depth-first. Shared prefixes are the whole point."""

META = {"slug": "_trie", "title": "Trie renderer", "pattern": "Fixture"}

VARIANTS = [
    {"id": "typical", "label": "Shared prefixes", "input": {"words": ["car", "cat", "cart", "dog"]}},
    {"id": "edge", "label": "One word", "input": {"words": ["a"]}},
]


def insert_all(words):
    root = {}
    for word in words:
        node = root
        for ch in word:
            #> Walk down if the letter exists, branch off if it doesn't.
            if ch not in node:
                node[ch] = {}
            node = node[ch]
        node["$"] = {}  #> A terminal marker: "cat" ends here even though "cart" continues.
    return len(words)


APPROACHES = [
    {
        "id": "insert",
        "label": "Insert words",
        "fn": insert_all,
        "complexity": {"time": "O(total chars)", "space": "O(total chars)"},
        "viz": {"root": "trie", "node": "trie"},
    }
]
