META = {
    "slug": "task-scheduler",
    "title": "Task Scheduler",
    "pattern": "Heap / Priority Queue",
    "difficulty": "Medium",
    "leetcode": 621,
    "prompt": "Identical tasks must be separated by at least n intervals of cooldown. Each task takes one interval. Return the fewest intervals needed to run them all, counting idle time.",
    "examples": [
        {"input": 'tasks = ["A","A","A","B","B","B"], n = 2', "output": "8",
         "why": "A B idle A B idle A B."},
        {"input": 'tasks = ["A","A","A","B","B","B"], n = 0', "output": "6", "why": "No cooldown, so no idling."},
    ],
    "constraints": ["1 <= len(tasks) <= 10^4", "0 <= n <= 100"],
}

VARIANTS = [
    {"id": "typical", "label": "With cooldown", "input": {"tasks": ["A", "A", "A", "B", "B", "B"], "n": 2}},
    {"id": "edge", "label": "No cooldown", "input": {"tasks": ["A", "A", "B"], "n": 0}},
    {"id": "worst-case", "label": "One dominant task", "input": {"tasks": ["A", "A", "A", "A", "B"], "n": 2}},
]


def from_the_busiest(tasks, n):
    counts = {}
    for t in tasks:
        counts[t] = counts.get(t, 0) + 1
    #> The most frequent task sets the skeleton: it needs (count - 1) gaps of
    #> n + 1 slots each, then one final run.
    busiest = 0
    for t in counts:
        busiest = max(busiest, counts[t])
    #> Several tasks tied at that frequency each add one slot to the last block.
    tied = 0
    for t in counts:
        if counts[t] == busiest:
            tied += 1
    frame = (busiest - 1) * (n + 1) + tied
    #> If there are enough other tasks to fill every gap, nothing idles at all,
    #> and the answer is simply the number of tasks.
    return max(frame, len(tasks))


APPROACHES = [
    {"id": "frame", "label": "Count from the busiest task", "fn": from_the_busiest,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"tasks": "array", "counts": "map"}},
]
