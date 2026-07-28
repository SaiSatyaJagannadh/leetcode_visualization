META = {
    "slug": "find-minimum-in-rotated-sorted-array",
    "title": "Find Minimum in Rotated Sorted Array",
    "pattern": "Binary Search",
    "difficulty": "Medium",
    "leetcode": 153,
    "prompt": "A sorted array of distinct values has been rotated some number of times. Find its smallest element in logarithmic time.",
    "examples": [
        {"input": "nums = [3,4,5,1,2]", "output": "1"},
        {"input": "nums = [11,13,15,17]", "output": "11", "why": "Rotated zero times, so it is still sorted."},
    ],
    "constraints": ["1 <= len(nums) <= 5000", "All values distinct"],
}

VARIANTS = [
    {"id": "typical", "label": "Rotated", "input": {"nums": [4, 5, 6, 7, 0, 1, 2]}},
    {"id": "edge", "label": "Not rotated", "input": {"nums": [11, 13, 15, 17]}},
    {"id": "worst-case", "label": "Rotated by one", "input": {"nums": [2, 3, 4, 5, 1]}},
]


def scan(nums):
    #> Reading every element works, but ignores everything the sorting tells us.
    best = nums[0]
    for i in range(len(nums)):
        if nums[i] < best:
            best = nums[i]  #> A new low; the rotation point is at or before here.
    return best


def binary(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        #> Comparing against the *right* end tells us which half is out of order,
        #> and the minimum always sits at the break.
        if nums[mid] > nums[hi]:
            #> mid is in the high run before the break, so the break is past mid.
            lo = mid + 1
        else:
            #> mid is at or after the break, so the answer is mid or to its left.
            hi = mid
    #> lo met hi exactly at the rotation point.
    return nums[lo]


APPROACHES = [
    {"id": "scan", "label": "Linear scan", "fn": scan,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"nums": "array", "i": "pointer:nums"}},
    {"id": "binary", "label": "Binary search", "fn": binary,
     "complexity": {"time": "O(log n)", "space": "O(1)"},
     "viz": {"nums": "array", "lo": "pointer:nums", "hi": "pointer:nums", "mid": "pointer:nums"}},
]
