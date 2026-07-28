META = {
    "slug": "find-median-from-data-stream",
    "title": "Find Median From Data Stream",
    "pattern": "Heap / Priority Queue",
    "difficulty": "Hard",
    "leetcode": 295,
    "prompt": "Numbers arrive one at a time. After each one, report the median of everything seen so far.",
    "examples": [
        {"input": "add 1, add 2, findMedian()", "output": "1.5"},
        {"input": "add 3, findMedian()", "output": "2.0"},
    ],
    "constraints": ["Up to 5 * 10^4 calls", "findMedian must be O(1)"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"stream": [1, 2, 3, 4, 5]}},
    {"id": "edge", "label": "Single value", "input": {"stream": [7]}},
    {"id": "worst-case", "label": "Descending", "input": {"stream": [9, 7, 5, 3]}},
]


def two_heaps(stream):
    #> `low` holds the smaller half as a max-heap (kept negated so the same
    #> min-heap code works), `high` holds the larger half. The median is always
    #> sitting on one or both of the two roots, so reading it is free.
    low = []
    high = []
    out = []
    for v in stream:
        #> Always offer to `low` first, then hand its largest over to `high`.
        #> That single funnel guarantees every value lands on the correct side.
        _push(low, -v)
        _push(high, -_pop(low))
        if len(high) > len(low):
            #> Keep `low` the same size or exactly one larger, so the odd-count
            #> median is always low's root.
            _push(low, -_pop(high))
        if len(low) > len(high):
            out.append(-low[0] * 1.0)
        else:
            out.append((-low[0] + high[0]) / 2.0)
    return out


def _push(heap, v):
    heap.append(v)
    i = len(heap) - 1
    while i > 0 and heap[(i - 1) // 2] > heap[i]:
        p = (i - 1) // 2
        heap[i], heap[p] = heap[p], heap[i]
        i = p


def _pop(heap):
    top = heap[0]
    heap[0] = heap[-1]
    heap.pop()
    i = 0
    while True:
        small = i
        for c in (2 * i + 1, 2 * i + 2):
            if c < len(heap) and heap[c] < heap[small]:
                small = c
        if small == i:
            break
        heap[i], heap[small] = heap[small], heap[i]
        i = small
    return top


APPROACHES = [
    {"id": "two-heaps", "label": "Two heaps facing each other", "fn": two_heaps,
     "complexity": {"time": "O(log n) per add", "space": "O(n)"},
     "viz": {"low": "heap", "high": "heap", "out": "queue", "stream": "array"}},
]
