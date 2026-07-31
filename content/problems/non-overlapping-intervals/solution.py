META = {
    "slug": "non-overlapping-intervals",
    "title": "Non-Overlapping Intervals",
    "pattern": "Intervals",
    "difficulty": "Medium",
    "leetcode": 435,
    "prompt": "Return the fewest intervals you must delete so that none of the survivors overlap.",
    "examples": [
        {"input": "intervals = [[1,2],[2,3],[3,4],[1,3]]", "output": "1"},
        {"input": "intervals = [[1,2],[1,2],[1,2]]", "output": "2"},
    ],
    "constraints": ["1 <= len(intervals) <= 10^5"],
}

VARIANTS = [
    {"id": "typical", "label": "Delete one", "input": {"intervals": [[1, 2], [2, 3], [3, 4], [1, 3]]}},
    {"id": "edge", "label": "All identical", "input": {"intervals": [[1, 2], [1, 2], [1, 2]]}},
    {"id": "worst-case", "label": "Already clean", "input": {"intervals": [[1, 2], [3, 4]]}},
]


def keep_earliest_ends(intervals):
    #> Sort by *end*, not start. Keeping the interval that finishes soonest
    #> leaves the most room for everything after it — sorting by start would let
    #> one very long interval crowd out several short ones.
    spans = sorted(intervals, key=lambda s: s[1])
    removed = 0
    last_end = None
    for span in spans:
        if last_end is None or span[0] >= last_end:
            #> Fits after the last one we kept, so keep it too.
            last_end = span[1]
        else:
            #> Overlaps. Dropping this one is never worse than dropping the
            #> earlier-ending one we already kept.
            removed += 1
    return removed


def longest_chain(intervals):
    #> Turn it around: instead of counting what to delete, count the largest set
    #> that can be kept, and subtract. Sorting by start makes this a longest
    #> increasing chain, which is the same problem wearing a different hat.
    spans = sorted(intervals, key=lambda s: s[0])
    keep = [1] * len(spans)
    best = 0
    for i in range(len(spans)):
        for j in range(i):
            #> span j can precede span i only if it finishes before i begins.
            if spans[j][1] <= spans[i][0] and keep[j] + 1 > keep[i]:
                keep[i] = keep[j] + 1
        if keep[i] > best:
            best = keep[i]
    #> Everything not in the longest keepable chain has to go.
    return len(spans) - best


APPROACHES = [
    {"id": "longest-chain", "label": "Keep the longest chain", "fn": longest_chain,
     "complexity": {"time": "O(n\u00b2)", "space": "O(n)"},
     "viz": {"intervals": "intervals", "spans": "intervals", "keep": "array", "i": "pointer:keep", "j": "pointer:keep"}},
    {"id": "earliest-end", "label": "Keep the earliest finisher", "fn": keep_earliest_ends,
     "complexity": {"time": "O(n log n)", "space": "O(n)"},
     "viz": {"intervals": "intervals", "spans": "intervals", "span": "interval"}},
]
