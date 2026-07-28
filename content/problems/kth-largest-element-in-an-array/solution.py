META = {
    "slug": "kth-largest-element-in-an-array",
    "title": "Kth Largest Element in an Array",
    "pattern": "Heap / Priority Queue",
    "difficulty": "Medium",
    "leetcode": 215,
    "prompt": "Return the kth largest value in an array, counting duplicates as separate entries.",
    "examples": [
        {"input": "nums = [3,2,1,5,6,4], k = 2", "output": "5"},
        {"input": "nums = [3,2,3,1,2,4,5,5,6], k = 4", "output": "4"},
    ],
    "constraints": ["1 <= k <= len(nums) <= 10^5"],
}

VARIANTS = [
    {"id": "typical", "label": "k = 2", "input": {"nums": [3, 2, 1, 5, 6, 4], "k": 2}},
    {"id": "edge", "label": "Largest", "input": {"nums": [3, 1, 2], "k": 1}},
    {"id": "worst-case", "label": "With duplicates", "input": {"nums": [3, 2, 3, 1, 2, 4], "k": 4}},
]


def sort_then_index(nums, k):
    #> Sorting answers it, but orders the whole array when only one slot matters.
    ordered = sorted(nums)
    return ordered[len(ordered) - k]


def min_heap_of_k(nums, k):
    #> Hold the k largest seen so far. The root is the weakest of them, so it is
    #> the kth largest once every value has been offered.
    heap = []
    for v in nums:
        heap.append(v)
        i = len(heap) - 1
        while i > 0 and heap[(i - 1) // 2] > heap[i]:
            p = (i - 1) // 2
            heap[i], heap[p] = heap[p], heap[i]
            i = p
        if len(heap) > k:
            #> Drop the smallest: k bigger values exist, so it is out of contention.
            heap[0] = heap[-1]
            heap.pop()
            j = 0
            while True:
                small = j
                for c in (2 * j + 1, 2 * j + 2):
                    if c < len(heap) and heap[c] < heap[small]:
                        small = c
                if small == j:
                    break
                heap[j], heap[small] = heap[small], heap[j]
                j = small
    return heap[0]


APPROACHES = [
    {"id": "sort", "label": "Sort and index", "fn": sort_then_index,
     "complexity": {"time": "O(n log n)", "space": "O(n)"},
     "viz": {"nums": "array", "ordered": "array"}},
    {"id": "heap", "label": "Min-heap of size k", "fn": min_heap_of_k,
     "complexity": {"time": "O(n log k)", "space": "O(k)"},
     "viz": {"nums": "array", "heap": "heap"}},
]
