META = {
    "slug": "search-in-rotated-sorted-array",
    "title": "Search in Rotated Sorted Array",
    "pattern": "Binary Search",
    "difficulty": "Medium",
    "leetcode": 33,
    "prompt": "A sorted array of distinct values has been rotated. Return the index of a target, or -1 if it isn't present, in logarithmic time.",
    "examples": [
        {"input": "nums = [4,5,6,7,0,1,2], target = 0", "output": "4"},
        {"input": "nums = [4,5,6,7,0,1,2], target = 3", "output": "-1"},
    ],
    "constraints": ["1 <= len(nums) <= 5000", "All values distinct"],
}

VARIANTS = [
    {"id": "typical", "label": "Found", "input": {"nums": [4, 5, 6, 7, 0, 1, 2], "target": 0}},
    {"id": "edge", "label": "Missing", "input": {"nums": [4, 5, 6, 7, 0, 1, 2], "target": 3}},
    {"id": "worst-case", "label": "First element", "input": {"nums": [5, 1, 2, 3, 4], "target": 5}},
]


def binary(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        #> A rotated array always has one half still properly sorted. Find which,
        #> and then the ordinary "is the target inside this range" test applies.
        if nums[lo] <= nums[mid]:
            #> Left half is clean.
            if nums[lo] <= target < nums[mid]:
                hi = mid - 1  #> Target lies inside the clean half.
            else:
                lo = mid + 1  #> So it must be in the messy half.
        else:
            #> Right half is the clean one instead.
            if nums[mid] < target <= nums[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1


APPROACHES = [
    {"id": "binary", "label": "Binary search the clean half", "fn": binary,
     "complexity": {"time": "O(log n)", "space": "O(1)"},
     "viz": {"nums": "array", "lo": "pointer:nums", "hi": "pointer:nums", "mid": "pointer:nums"}},
]
