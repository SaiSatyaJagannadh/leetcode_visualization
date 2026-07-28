META = {
    "slug": "binary-search",
    "title": "Binary Search",
    "pattern": "Binary Search",
    "difficulty": "Easy",
    "leetcode": 704,
    "prompt": (
        "Given a sorted array of distinct integers and a target, return the index "
        "of the target, or -1 if it isn't there. The search must run in logarithmic "
        "time."
    ),
    "examples": [
        {"input": "nums = [-1,0,3,5,9,12], target = 9", "output": "4"},
        {"input": "nums = [-1,0,3,5,9,12], target = 2", "output": "-1",
         "why": "2 would sit between 0 and 3, so it isn't present."},
    ],
    "constraints": ["1 <= len(nums) <= 10^4", "nums is sorted ascending, all distinct"],
}

VARIANTS = [
    {"id": "typical", "label": "Found", "input": {"nums": [-1, 0, 3, 5, 9, 12], "target": 9}},
    {"id": "edge", "label": "Missing", "input": {"nums": [-1, 0, 3, 5, 9, 12], "target": 2}},
    {
        "id": "worst-case",
        "label": "First element",
        "input": {"nums": [1, 3, 5, 7, 9, 11, 13, 15], "target": 1},
    },
]


def linear(nums, target):
    for i in range(len(nums)):
        #> Checking every slot works, but throws away the fact that nums is sorted.
        if nums[i] == target:
            return i
    return -1


def binary(nums, target):
    lo = 0
    hi = len(nums) - 1
    while lo <= hi:
        #> Look at the middle of what's left, never the middle of the whole array.
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            #> Sorted order guarantees the target can't be at or left of mid.
            lo = mid + 1
        else:
            #> Same argument mirrored: everything from mid rightward is too large.
            hi = mid - 1
    #> lo passed hi, so the window is empty and the target was never there.
    return -1


APPROACHES = [
    {
        "id": "linear",
        "label": "Linear scan",
        "fn": linear,
        "complexity": {"time": "O(n)", "space": "O(1)"},
        "viz": {"nums": "array", "i": "pointer:nums"},
    },
    {
        "id": "binary",
        "label": "Binary search",
        "fn": binary,
        "complexity": {"time": "O(log n)", "space": "O(1)"},
        "viz": {"nums": "array", "lo": "pointer:nums", "hi": "pointer:nums", "mid": "pointer:nums"},
    },
]
