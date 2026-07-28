META = {
    "slug": "kth-largest-element-in-a-stream",
    "title": "Kth Largest Element in a Stream",
    "pattern": "Heap / Priority Queue",
    "difficulty": "Easy",
    "leetcode": 703,
    "prompt": "Numbers arrive one at a time. After each arrival, report the kth largest value seen so far.",
    "examples": [
        {"input": "k = 3, nums = [4,5,8,2], then add 3", "output": "4"},
        {"input": "then add 5", "output": "5"},
    ],
    "constraints": ["1 <= k <= 10^4", "There are always at least k values when asked"],
}

VARIANTS = [
    {"id": "typical", "label": "k = 3", "input": {"k": 3, "stream": [4, 5, 8, 2, 3, 5, 10]}},
    {"id": "edge", "label": "k = 1", "input": {"k": 1, "stream": [5, 2, 9]}},
    {"id": "worst-case", "label": "Descending stream", "input": {"k": 2, "stream": [9, 8, 7, 6]}},
]


def min_heap_of_k(k, stream):
    #> Keep only the k largest values, in a min-heap. Its root is therefore the
    #> smallest of the top k — which is exactly the kth largest overall.
    heap = []
    out = []
    for v in stream:
        _push(heap, v)
        if len(heap) > k:
            #> Over capacity, so evict the smallest. It can never be the answer
            #> again, because k larger values already exist.
            _pop(heap)
        out.append(heap[0] if len(heap) == k else None)
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
    {"id": "min-heap", "label": "Min-heap of size k", "fn": min_heap_of_k,
     "complexity": {"time": "O(log k) per add", "space": "O(k)"},
     "viz": {"heap": "heap", "out": "queue", "stream": "array"}},
]
