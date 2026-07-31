META = {
    "slug": "meeting-rooms-ii",
    "title": "Meeting Rooms II",
    "pattern": "Intervals",
    "difficulty": "Medium",
    "leetcode": 253,
    "prompt": "Return the smallest number of rooms needed so that no two meetings share a room at the same time.",
    "examples": [
        {"input": "intervals = [[0,30],[5,10],[15,20]]", "output": "2"},
        {"input": "intervals = [[7,10],[2,4]]", "output": "1"},
    ],
    "constraints": ["1 <= len(intervals) <= 10^4"],
}

VARIANTS = [
    {"id": "typical", "label": "Two rooms", "input": {"intervals": [[0, 30], [5, 10], [15, 20]]}},
    {"id": "edge", "label": "One room", "input": {"intervals": [[7, 10], [2, 4]]}},
    {"id": "worst-case", "label": "All at once", "input": {"intervals": [[1, 9], [2, 8], [3, 7]]}},
]


def sweep_events(intervals):
    #> Forget which meeting is which. Sort the starts and the ends separately and
    #> sweep the clock: the answer is just the busiest moment.
    starts = sorted(s[0] for s in intervals)
    ends = sorted(s[1] for s in intervals)
    rooms = 0
    best = 0
    i = 0
    j = 0
    while i < len(starts):
        if starts[i] < ends[j]:
            #> A meeting begins before the earliest one ends, so a room is claimed.
            rooms += 1
            i += 1
            if rooms > best:
                best = rooms
        else:
            #> The earliest-ending meeting finishes, freeing its room.
            rooms -= 1
            j += 1
    return best


def busiest_moment(intervals):
    #> The peak can only happen when a meeting starts — nothing gets busier in
    #> the middle of one. So check each start time and count what is running.
    best = 0
    for a in intervals:
        moment = a[0]
        running = 0
        for b in intervals:
            #> Running at this instant: already begun, not yet finished. A
            #> meeting ending exactly now has released its room.
            if b[0] <= moment and moment < b[1]:
                running += 1
        if running > best:
            best = running
    return best


APPROACHES = [
    {"id": "brute-force", "label": "Count at every start", "fn": busiest_moment,
     "complexity": {"time": "O(n\u00b2)", "space": "O(1)"},
     "viz": {"intervals": "intervals"}},
    {"id": "sweep", "label": "Sweep starts against ends", "fn": sweep_events,
     "complexity": {"time": "O(n log n)", "space": "O(n)"},
     "viz": {"intervals": "intervals", "starts": "array", "ends": "array", "i": "pointer:starts", "j": "pointer:ends"}},
]
