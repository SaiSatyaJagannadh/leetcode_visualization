META = {
    "slug": "meeting-rooms",
    "title": "Meeting Rooms",
    "pattern": "Intervals",
    "difficulty": "Easy",
    "leetcode": 252,
    "prompt": "Given a list of meeting times, decide whether one person could attend all of them without a clash.",
    "examples": [
        {"input": "intervals = [[0,30],[5,10],[15,20]]", "output": "false"},
        {"input": "intervals = [[7,10],[2,4]]", "output": "true"},
    ],
    "constraints": ["0 <= len(intervals) <= 10^4"],
}

VARIANTS = [
    {"id": "typical", "label": "Clashes", "input": {"intervals": [[0, 30], [5, 10], [15, 20]]}},
    {"id": "edge", "label": "No clash", "input": {"intervals": [[7, 10], [2, 4]]}},
    {"id": "worst-case", "label": "Touching is fine", "input": {"intervals": [[1, 5], [5, 8]]}},
]


def sort_and_compare(intervals):
    #> Once sorted by start, a clash can only be between neighbours: if a meeting
    #> overlapped one further back, it would overlap its neighbour too.
    spans = sorted(intervals, key=lambda s: s[0])
    for i in range(1, len(spans)):
        if spans[i][0] < spans[i - 1][1]:
            #> Starts before the previous ends. Ending exactly as one starts is
            #> fine, hence strict less-than.
            return False
    return True


APPROACHES = [
    {"id": "sort", "label": "Sort, then check neighbours", "fn": sort_and_compare,
     "complexity": {"time": "O(n log n)", "space": "O(n)"},
     "viz": {"intervals": "intervals", "spans": "intervals", "i": "pointer:spans"}},
]
