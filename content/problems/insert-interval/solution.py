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


APPROACHES = [
    {"id": "three-phases", "label": "Before, overlapping, after", "fn": three_phases,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"intervals": "intervals", "out": "intervals", "merged": "interval", "new": "interval"}},
]
