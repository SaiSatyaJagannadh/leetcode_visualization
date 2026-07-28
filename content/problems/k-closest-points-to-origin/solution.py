META = {
    "slug": "k-closest-points-to-origin",
    "title": "K Closest Points to Origin",
    "pattern": "Heap / Priority Queue",
    "difficulty": "Medium",
    "leetcode": 973,
    "prompt": "Return the k points nearest the origin, measured by straight-line distance. The answer may be in any order.",
    "examples": [
        {"input": "points = [[1,3],[-2,2]], k = 1", "output": "[[-2,2]]"},
        {"input": "points = [[3,3],[5,-1],[-2,4]], k = 2", "output": "[[3,3],[-2,4]]"},
    ],
    "constraints": ["1 <= k <= len(points) <= 10^4"],
    "unordered": True,
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"points": [[1, 3], [-2, 2], [5, 8], [0, 1]], "k": 2}},
    {"id": "edge", "label": "k = all", "input": {"points": [[1, 1], [2, 2]], "k": 2}},
    {"id": "worst-case", "label": "Nearest last", "input": {"points": [[9, 9], [8, 8], [1, 0]], "k": 1}},
]


def sort_by_distance(points, k):
    #> Comparing squared distances avoids square roots and orders identically.
    ordered = sorted(points, key=lambda p: p[0] * p[0] + p[1] * p[1])
    return ordered[:k]


def max_heap_of_k(points, k):
    #> Keep the k best in a max-heap keyed by distance, so the root is the worst
    #> of the current best — the one to evict when something better shows up.
    heap = []
    for p in points:
        d = p[0] * p[0] + p[1] * p[1]
        heap.append([d, p[0], p[1]])
        i = len(heap) - 1
        while i > 0 and heap[(i - 1) // 2][0] < heap[i][0]:
            par = (i - 1) // 2
            heap[i], heap[par] = heap[par], heap[i]
            i = par
        if len(heap) > k:
            #> Evict the farthest; k nearer points already exist.
            heap[0] = heap[-1]
            heap.pop()
            j = 0
            while True:
                big = j
                for c in (2 * j + 1, 2 * j + 2):
                    if c < len(heap) and heap[c][0] > heap[big][0]:
                        big = c
                if big == j:
                    break
                heap[j], heap[big] = heap[big], heap[j]
                j = big
    out = []
    for entry in heap:
        out.append([entry[1], entry[2]])
    return out


APPROACHES = [
    {"id": "sort", "label": "Sort by distance", "fn": sort_by_distance,
     "complexity": {"time": "O(n log n)", "space": "O(n)"},
     "viz": {"points": "array", "ordered": "array"}},
    {"id": "heap", "label": "Max-heap of size k", "fn": max_heap_of_k,
     "complexity": {"time": "O(n log k)", "space": "O(k)"},
     "viz": {"points": "array", "heap": "array", "out": "array"}},
]
