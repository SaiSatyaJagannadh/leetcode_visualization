META = {
    "slug": "minimum-interval-to-include-each-query",
    "title": "Minimum Interval to Include Each Query",
    "pattern": "Intervals",
    "difficulty": "Hard",
    "leetcode": 1851,
    "prompt": "For each query point, return the size of the smallest interval that contains it, or -1 if none does.",
    "examples": [
        {"input": "intervals = [[1,4],[2,4],[3,6],[4,4]], queries = [2,3,4,5]", "output": "[3,3,1,4]"},
        {"input": "intervals = [[1,2]], queries = [5]", "output": "[-1]"},
    ],
    "constraints": ["1 <= len(intervals), len(queries) <= 10^5"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"intervals": [[1, 4], [2, 4], [3, 6], [4, 4]], "queries": [2, 3, 4, 5]}},
    {"id": "edge", "label": "Nothing contains it", "input": {"intervals": [[1, 2]], "queries": [5]}},
    {"id": "worst-case", "label": "Nested intervals", "input": {"intervals": [[1, 10], [2, 5], [3, 4]], "queries": [3]}},
]

BIG = 10 ** 9


def per_query_scan(intervals, queries):
    out = []
    for q in queries:
        #> For each query, look at every interval and keep the smallest that
        #> covers it. Clear, and fine when either list is short.
        best = BIG
        for span in intervals:
            if span[0] <= q <= span[1]:
                size = span[1] - span[0] + 1
                if size < best:
                    best = size
        out.append(-1 if best == BIG else best)
    return out


def sorted_sweep(intervals, queries):
    #> Sorting both lists means each interval is opened once, in order, rather
    #> than re-examined for every query.
    spans = sorted(intervals, key=lambda s: s[0])
    order = sorted(range(len(queries)), key=lambda i: queries[i])
    answers = [-1] * len(queries)
    live = []
    i = 0
    for qi in order:
        q = queries[qi]
        #> Open every interval that has started by now.
        while i < len(spans) and spans[i][0] <= q:
            live.append(spans[i])
            i += 1
        #> Drop the ones that already ended — they can't cover this or any later
        #> query, since queries only move forward.
        live = [s for s in live if s[1] >= q]
        best = BIG
        for s in live:
            size = s[1] - s[0] + 1
            if size < best:
                best = size
        answers[qi] = -1 if best == BIG else best
    return answers


APPROACHES = [
    {"id": "scan", "label": "Scan every interval per query", "fn": per_query_scan,
     "complexity": {"time": "O(nq)", "space": "O(1)"},
     "viz": {"intervals": "intervals", "out": "queue", "queries": "array"}},
    {"id": "sweep", "label": "Sort both, sweep once", "fn": sorted_sweep,
     "complexity": {"time": "O(n log n + q log q)", "space": "O(n)"},
     "viz": {"spans": "intervals", "live": "intervals", "answers": "array", "queries": "array"}},
]
