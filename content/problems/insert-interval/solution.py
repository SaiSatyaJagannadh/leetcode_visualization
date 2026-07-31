META = {
    "slug": "insert-interval",
    "title": "Insert Interval",
    "pattern": "Intervals",
    "difficulty": "Medium",
    "leetcode": 57,
    "prompt": "Insert a new interval into a list that is already sorted and non-overlapping, merging anything it runs into. Return the result still sorted.",
    "examples": [
        {"input": "intervals = [[1,3],[6,9]], newInterval = [2,5]", "output": "[[1,5],[6,9]]"},
        {"input": "intervals = [[1,5]], newInterval = [6,8]", "output": "[[1,5],[6,8]]"},
    ],
    "constraints": ["0 <= len(intervals) <= 10^4", "intervals is sorted by start"],
}

VARIANTS = [
    {"id": "typical", "label": "Merges one", "input": {"intervals": [[1, 3], [6, 9]], "new": [2, 5]}},
    {"id": "edge", "label": "No overlap", "input": {"intervals": [[1, 5]], "new": [6, 8]}},
    {"id": "worst-case", "label": "Swallows several", "input": {"intervals": [[1, 2], [3, 5], [6, 7], [8, 10]], "new": [4, 9]}},
]


def three_phases(intervals, new):
    out = []
    i = 0
    n = len(intervals)
    #> Phase one: everything ending before the new interval starts is untouched.
    while i < n and intervals[i][1] < new[0]:
        out.append(intervals[i])
        i += 1
    #> Phase two: absorb every interval that overlaps, widening as we go. The
    #> input being sorted is what makes these form one contiguous run.
    merged = [new[0], new[1]]
    while i < n and intervals[i][0] <= merged[1]:
        merged[0] = min(merged[0], intervals[i][0])
        merged[1] = max(merged[1], intervals[i][1])
        i += 1
    out.append(merged)
    #> Phase three: the rest start after the merged block, so they follow as-is.
    while i < n:
        out.append(intervals[i])
        i += 1
    return out


def append_and_merge(intervals, new):
    #> The blunt version: drop the new interval in, sort everything, then merge
    #> in one sweep. It ignores the fact that the input was already sorted, which
    #> is exactly the information the three-phase walk exploits.
    spans = [[s[0], s[1]] for s in intervals]
    spans.append([new[0], new[1]])
    spans = sorted(spans, key=lambda s: s[0])
    out = []
    for span in spans:
        if out and span[0] <= out[-1][1]:
            #> Overlaps what we are building, so widen it rather than adding.
            out[-1] = [out[-1][0], max(out[-1][1], span[1])]
        else:
            #> A clean gap; nothing later can reach back past it.
            out.append([span[0], span[1]])
    return out


APPROACHES = [
    {"id": "sort-merge", "label": "Append, sort, merge", "fn": append_and_merge,
     "complexity": {"time": "O(n log n)", "space": "O(n)"},
     "viz": {"intervals": "intervals", "spans": "intervals", "out": "intervals"}},
    {"id": "three-phases", "label": "Before, overlapping, after", "fn": three_phases,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"intervals": "intervals", "out": "intervals", "merged": "interval", "new": "interval"}},
]
