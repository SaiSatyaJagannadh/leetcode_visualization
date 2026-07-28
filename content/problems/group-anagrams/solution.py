META = {
    "slug": "group-anagrams",
    "title": "Group Anagrams",
    "pattern": "Arrays & Hashing",
    "difficulty": "Medium",
    "leetcode": 49,
    "prompt": "Given a list of strings, gather the ones that are rearrangements of each other into groups. Return the groups in any order.",
    "examples": [
        {"input": 'strs = ["eat","tea","tan","ate","nat","bat"]',
         "output": '[["eat","tea","ate"],["tan","nat"],["bat"]]'},
        {"input": 'strs = [""]', "output": '[[""]]'},
    ],
    "constraints": ["1 <= len(strs) <= 10^4", "Lowercase English letters"],
}

VARIANTS = [
    {"id": "typical", "label": "Three groups", "input": {"strs": ["eat", "tea", "tan", "ate", "nat", "bat"]}},
    {"id": "edge", "label": "No group larger than one", "input": {"strs": ["abc", "def"]}},
    {"id": "worst-case", "label": "All one group", "input": {"strs": ["abc", "bca", "cab"]}},
]


def by_sorted_key(strs):
    #> Anagrams differ only in order, so sorting a word yields a fingerprint that
    #> every member of the group shares and no outsider can produce.
    groups = {}
    for word in strs:
        key = "".join(sorted(word))
        if key not in groups:
            #> First word with this fingerprint starts a new group.
            groups[key] = []
        groups[key].append(word)
    out = []
    for key in groups:
        out.append(groups[key])
    return out


def by_letter_counts(strs):
    #> Same idea without sorting: a 26-slot tally is just as unique a fingerprint
    #> and costs one pass over the word instead of n log n.
    groups = {}
    for word in strs:
        counts = [0] * 26
        for ch in word:
            counts[ord(ch) - 97] += 1
        key = ",".join(str(c) for c in counts)
        if key not in groups:
            groups[key] = []
        groups[key].append(word)
    out = []
    for key in groups:
        out.append(groups[key])
    return out


APPROACHES = [
    {"id": "sorted-key", "label": "Sorted-word key", "fn": by_sorted_key,
     "complexity": {"time": "O(n k log k)", "space": "O(nk)"},
     "viz": {"strs": "array", "word": "array"}},
    {"id": "count-key", "label": "Letter-count key", "fn": by_letter_counts,
     "complexity": {"time": "O(nk)", "space": "O(nk)"},
     "viz": {"strs": "array", "counts": "array"}},
]
