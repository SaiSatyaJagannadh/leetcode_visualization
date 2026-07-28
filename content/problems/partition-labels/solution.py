META = {
    "slug": "partition-labels",
    "title": "Partition Labels",
    "pattern": "Greedy",
    "difficulty": "Medium",
    "leetcode": 763,
    "prompt": "Cut the string into as many pieces as possible so that each letter appears in only one piece. Return the piece sizes in order.",
    "examples": [
        {"input": 's = "ababcbacadefegde"', "output": "[9,7]"},
        {"input": 's = "abc"', "output": "[1,1,1]"},
    ],
    "constraints": ["1 <= len(s) <= 500", "Lowercase English letters"],
}

VARIANTS = [
    {"id": "typical", "label": "Two pieces", "input": {"s": "ababcbacadefegde"}},
    {"id": "edge", "label": "All distinct", "input": {"s": "abc"}},
    {"id": "worst-case", "label": "One piece", "input": {"s": "abcabc"}},
]


def last_occurrence(s):
    #> Where each letter appears for the final time. A piece can't close before
    #> the last copy of every letter it already contains.
    last = {}
    for i in range(len(s)):
        last[s[i]] = i
    out = []
    start = 0
    end = 0
    for i in range(len(s)):
        #> Seeing a letter pushes the piece's end out to that letter's last copy.
        if last[s[i]] > end:
            end = last[s[i]]
        if i == end:
            #> Reached the furthest commitment, so nothing inside recurs later.
            out.append(end - start + 1)
            start = i + 1
    return out


APPROACHES = [
    {"id": "last", "label": "Extend to the last occurrence", "fn": last_occurrence,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"s": "array", "last": "map", "i": "pointer:s", "end": "pointer:s", "out": "queue"}},
]
