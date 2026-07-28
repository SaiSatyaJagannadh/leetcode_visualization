META = {
    "slug": "last-stone-weight",
    "title": "Last Stone Weight",
    "pattern": "Heap / Priority Queue",
    "difficulty": "Easy",
    "leetcode": 1046,
    "prompt": (
        "Repeatedly smash the two heaviest stones together. Equal stones destroy "
        "each other; otherwise the heavier one survives with the difference in "
        "weight. Return the last stone's weight, or 0 if none remain."
    ),
    "examples": [
        {"input": "stones = [2,7,4,1,8,1]", "output": "1",
         "why": "8 and 7 leave 1; then 4 and 2 leave 2; then 2 and 1 leave 1; then 1 and 1 cancel."},
        {"input": "stones = [1]", "output": "1", "why": "Nothing to smash it against."},
    ],
    "constraints": ["1 <= len(stones) <= 30", "1 <= stones[i] <= 1000"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"stones": [2, 7, 4, 1, 8, 1]}},
    {"id": "edge", "label": "All cancel", "input": {"stones": [3, 3]}},
    {"id": "worst-case", "label": "One survivor", "input": {"stones": [5, 4, 3, 2, 1]}},
]


def sort_each_round(stones):
    pile = list(stones)
    while len(pile) > 1:
        #> Re-sorting every round is correct but does far more work than needed:
        #> we only ever want the top two.
        pile.sort()
        big = pile.pop()
        second = pile.pop()
        if big != second:
            pile.append(big - second)  #> The survivor rejoins the pile, lighter.
    return pile[0] if pile else 0


def max_heap(stones):
    #> A max-heap kept as a list: heap[0] is always the heaviest stone, and
    #> restoring that after a change costs log n instead of a full re-sort.
    heap = []
    for s in stones:
        heap.append(s)
        i = len(heap) - 1
        while i > 0 and heap[(i - 1) // 2] < heap[i]:
            #> Sift up: the newcomer outweighs its parent, so they trade places.
            p = (i - 1) // 2
            heap[i], heap[p] = heap[p], heap[i]
            i = p

    while len(heap) > 1:
        first = _pop(heap)  #> The heaviest stone.
        second = _pop(heap)  #> And the next heaviest, now that the first is gone.
        if first != second:
            #> The survivor is a brand new weight, so it has to find its own place.
            _push(heap, first - second)
    return heap[0] if heap else 0


def _pop(heap):
    top = heap[0]
    heap[0] = heap[-1]
    heap.pop()
    i = 0
    while True:
        big = i
        for c in (2 * i + 1, 2 * i + 2):
            if c < len(heap) and heap[c] > heap[big]:
                big = c
        if big == i:
            break
        heap[i], heap[big] = heap[big], heap[i]
        i = big
    return top


def _push(heap, v):
    heap.append(v)
    i = len(heap) - 1
    while i > 0 and heap[(i - 1) // 2] < heap[i]:
        p = (i - 1) // 2
        heap[i], heap[p] = heap[p], heap[i]
        i = p


APPROACHES = [
    {
        "id": "sort",
        "label": "Re-sort each round",
        "fn": sort_each_round,
        "complexity": {"time": "O(n² log n)", "space": "O(n)"},
        "viz": {"pile": "array", "stones": "array"},
    },
    {
        "id": "heap",
        "label": "Max-heap",
        "fn": max_heap,
        "complexity": {"time": "O(n log n)", "space": "O(n)"},
        "viz": {"heap": "heap", "i": "pointer:heap", "stones": "array"},
    },
]
