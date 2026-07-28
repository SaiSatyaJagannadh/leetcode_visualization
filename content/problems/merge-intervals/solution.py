META = {
    "slug": "merge-intervals",
    "title": "Merge Intervals",
    "pattern": "Intervals",
    "difficulty": "Medium",
    "leetcode": 56,
    "prompt": (
        "Given a list of intervals, combine every group that overlaps into a "
        "single interval and return the result. Intervals that merely touch at "
        "an endpoint count as overlapping."
    ),
    "examples": [
        {"input": "intervals = [[1,3],[2,6],[8,10],[15,18]]", "output": "[[1,6],[8,10],[15,18]]",
         "why": "[1,3] and [2,6] overlap, so they become [1,6]."},
        {"input": "intervals = [[1,4],[4,5]]", "output": "[[1,5]]",
         "why": "They touch at 4, which still counts."},
    ],
    "constraints": ["1 <= len(intervals) <= 10^4", "start <= end for every interval"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"intervals": [[1, 3], [2, 6], [8, 10], [15, 18]]}},
    {"id": "edge", "label": "Nested", "input": {"intervals": [[1, 10], [3, 5]]}},
    {
        "id": "worst-case",
        "label": "Reverse order",
        "input": {"intervals": [[15, 18], [8, 10], [2, 6], [1, 3], [5, 9]]},
    },
]


def sweep(intervals):
    #> Sorting by start is the whole trick: after this, anything that overlaps the
    #> interval we're building must start before it ends, so one pass is enough.
    spans = sorted(intervals, key=lambda s: s[0])
    out = []
    for span in spans:
        if out and span[0] <= out[-1][1]:
            #> Overlaps the last kept interval, so widen that one instead of adding.
            out[-1] = [out[-1][0], max(out[-1][1], span[1])]
        else:
            #> A clean gap. Nothing later can reach back past it, so close and move on.
            out.append([span[0], span[1]])
    return out


def brute_force(intervals):
    out = [[s[0], s[1]] for s in intervals]
    merged = True
    while merged:
        #> Without sorting, one pass isn't enough — keep sweeping until nothing changes.
        merged = False
        for i in range(len(out)):
            for j in range(i + 1, len(out)):
                a, b = out[i], out[j]
                #> Two intervals overlap unless one ends entirely before the other starts.
                if a[0] <= b[1] and b[0] <= a[1]:
                    out[i] = [min(a[0], b[0]), max(a[1], b[1])]
                    out.pop(j)
                    merged = True  #> Something changed, so another pass is needed.
                    break
            if merged:
                break
    return out


APPROACHES = [
    {
        "id": "sweep",
        "label": "Sort and sweep",
        "fn": sweep,
        "complexity": {"time": "O(n log n)", "space": "O(n)"},
        "viz": {"intervals": "intervals", "spans": "intervals", "out": "intervals", "span": "interval"},
    },
    {
        "id": "brute-force",
        "label": "Merge until stable",
        "fn": brute_force,
        "complexity": {"time": "O(n³)", "space": "O(n)"},
        "viz": {"intervals": "intervals", "out": "intervals"},
    },
]
