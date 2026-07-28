META = {
    "slug": "sliding-window-maximum",
    "title": "Sliding Window Maximum",
    "pattern": "Sliding Window",
    "difficulty": "Hard",
    "leetcode": 239,
    "prompt": "A window of width k slides across the array one position at a time. Return the maximum inside the window at each stop.",
    "examples": [
        {"input": "nums = [1,3,-1,-3,5,3,6,7], k = 3", "output": "[3,3,5,5,6,7]"},
        {"input": "nums = [1], k = 1", "output": "[1]"},
    ],
    "constraints": ["1 <= len(nums) <= 10^5", "1 <= k <= len(nums)"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"nums": [1, 3, -1, -3, 5, 3], "k": 3}},
    {"id": "edge", "label": "Window of one", "input": {"nums": [4, 2, 7], "k": 1}},
    {"id": "worst-case", "label": "Descending", "input": {"nums": [9, 8, 7, 6, 5], "k": 2}},
]


def rescan(nums, k):
    out = []
    for i in range(len(nums) - k + 1):
        #> Re-reading the whole window each stop repeats most of the work.
        best = nums[i]
        for j in range(i, i + k):
            best = max(best, nums[j])
        out.append(best)
    return out


def monotonic_deque(nums, k):
    #> The deque holds indices whose values decrease from front to back, so the
    #> front is always the window's maximum.
    dq = []
    out = []
    for i in range(len(nums)):
        #> A smaller value behind a larger one can never be a future maximum while
        #> the larger one is still in the window, so drop it for good.
        while dq and nums[dq[-1]] <= nums[i]:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            #> The front has slid out of the window's left edge.
            dq.pop(0)
        if i >= k - 1:
            out.append(nums[dq[0]])  #> Window is full, so record its maximum.
    return out


APPROACHES = [
    {"id": "rescan", "label": "Rescan each window", "fn": rescan,
     "complexity": {"time": "O(nk)", "space": "O(1)"},
     "viz": {"nums": "array", "i": "pointer:nums", "j": "pointer:nums", "out": "queue"}},
    {"id": "deque", "label": "Monotonic deque", "fn": monotonic_deque,
     "complexity": {"time": "O(n)", "space": "O(k)"},
     "viz": {"nums": "array", "i": "pointer:nums", "dq": "queue", "out": "queue"}},
]
