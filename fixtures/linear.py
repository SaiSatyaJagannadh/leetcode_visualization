"""Stack, queue, heap and bits — all array-shaped, all one renderer with markers.

Heap is the interesting one: sift-up and sift-down are swaps, and the tree view
is derived from array indices, so it needs no baked coordinates.
"""

META = {"slug": "_linear", "title": "Stack / queue / heap / bits", "pattern": "Fixture"}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"vals": [5, 3, 8, 1, 9, 2], "text": "([{}])"}},
    {"id": "edge", "label": "Already ordered", "input": {"vals": [1, 2, 3], "text": "(]"}},
]


def valid_parens(vals, text):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in text:
        if ch in pairs:
            #> A closer only matches if the top of the stack is its partner.
            if not stack or stack[-1] != pairs[ch]:
                return False
            stack.pop()  #> Matched, so the pair disappears from the stack.
        else:
            stack.append(ch)  #> An opener waits on the stack for its closer.
    return len(stack) == 0


def heap_push_pop(vals, text):
    heap = []
    for v in vals:
        heap.append(v)
        i = len(heap) - 1
        while i > 0 and heap[(i - 1) // 2] > heap[i]:
            #> Sift up: the new value is smaller than its parent, so they swap.
            p = (i - 1) // 2
            heap[i], heap[p] = heap[p], heap[i]
            i = p
    out = []
    while heap:
        out.append(heap[0])  #> The root is always the smallest value left.
        heap[0] = heap[-1]
        heap.pop()
        i = 0
        while True:
            #> Sift down: swap with the smaller child until the order holds again.
            small = i
            for c in (2 * i + 1, 2 * i + 2):
                if c < len(heap) and heap[c] < heap[small]:
                    small = c
            if small == i:
                break
            heap[i], heap[small] = heap[small], heap[i]
            i = small
    return out


def count_bits(vals, text):
    total = 0
    for v in vals:
        bits = []
        n = v
        while n > 0:
            bits.append(n & 1)  #> Read the lowest bit, then shift it away.
            n = n >> 1
        #> Reversed, the collected bits read as the binary number.
        bits.reverse()
        total += sum(bits)
    return total


APPROACHES = [
    {
        "id": "stack",
        "label": "Stack",
        "fn": valid_parens,
        "complexity": {"time": "O(n)", "space": "O(n)"},
        "viz": {"stack": "stack", "text": "array"},
    },
    {
        "id": "heap",
        "label": "Heap",
        "fn": heap_push_pop,
        "complexity": {"time": "O(n log n)", "space": "O(n)"},
        "viz": {"heap": "heap", "i": "pointer:heap", "out": "queue"},
    },
    {
        "id": "bits",
        "label": "Bits",
        "fn": count_bits,
        "complexity": {"time": "O(n log v)", "space": "O(1)"},
        "viz": {"bits": "bits", "vals": "array"},
    },
]
