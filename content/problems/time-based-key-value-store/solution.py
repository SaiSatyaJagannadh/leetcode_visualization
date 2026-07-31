META = {
    "slug": "time-based-key-value-store",
    "title": "Time Based Key-Value Store",
    "pattern": "Binary Search",
    "difficulty": "Medium",
    "leetcode": 981,
    "prompt": "Store values against a key with a timestamp, then look up the value that was current at any given time — the most recent write at or before it.",
    "examples": [
        {"input": 'set("foo","bar",1), get("foo",1)', "output": '"bar"'},
        {"input": 'get("foo",3)', "output": '"bar"', "why": "No write at 3, so the write at 1 still stands."},
        {"input": 'get("foo",0)', "output": '""', "why": "Nothing had been written yet."},
    ],
    "constraints": ["Timestamps for a key strictly increase", "get must be logarithmic"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"writes": [[1, "a"], [4, "b"], [7, "c"]], "queries": [1, 3, 5, 9]}},
    {"id": "edge", "label": "Before any write", "input": {"writes": [[5, "x"]], "queries": [1, 5]}},
    {"id": "worst-case", "label": "Exact hits", "input": {"writes": [[1, "a"], [2, "b"], [3, "c"]], "queries": [3, 2, 1]}},
]


def store(writes, queries):
    #> Writes arrive with increasing timestamps, so the log is already sorted —
    #> which is the only reason binary search is available here.
    log = []
    for w in writes:
        log.append(w)
    out = []
    for t in queries:
        lo, hi = 0, len(log) - 1
        answer = ""
        while lo <= hi:
            mid = (lo + hi) // 2
            if log[mid][0] <= t:
                #> This write is old enough to count. Remember it, but keep looking
                #> right in case a later write is still at or before t.
                answer = log[mid][1]
                lo = mid + 1
            else:
                #> Written after the query time, so it hadn't happened yet.
                hi = mid - 1
        out.append(answer)
    return out


def scan_backwards(writes, queries):
    #> No binary search: walk the log from the newest entry back and stop at the
    #> first one old enough. Correct without needing the log to be sorted at
    #> all — which is exactly the property binary search depends on.
    log = []
    for w in writes:
        log.append(w)
    out = []
    for t in queries:
        answer = ""
        for i in range(len(log) - 1, -1, -1):
            if log[i][0] <= t:
                #> Walking from the newest end means the first match IS the
                #> latest write at or before t.
                answer = log[i][1]
                break
        out.append(answer)
    return out


APPROACHES = [
    {"id": "scan", "label": "Walk back from the newest", "fn": scan_backwards,
     "complexity": {"time": "O(q \u00b7 n)", "space": "O(n)"},
     "viz": {"log": "array", "out": "queue", "i": "pointer:log"}},
    {"id": "binary", "label": "Binary search the log", "fn": store,
     "complexity": {"time": "O(log n) per get", "space": "O(n)"},
     "viz": {"log": "array", "out": "queue", "queries": "array", "lo": "pointer:log", "hi": "pointer:log", "mid": "pointer:log"}},
]
