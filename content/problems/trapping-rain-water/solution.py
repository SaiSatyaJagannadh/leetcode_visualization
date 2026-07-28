META = {
    "slug": "trapping-rain-water",
    "title": "Trapping Rain Water",
    "pattern": "Two Pointers",
    "difficulty": "Hard",
    "leetcode": 42,
    "prompt": "The array describes an elevation map where each bar is one unit wide. After rain, how much water is trapped between the bars?",
    "examples": [
        {"input": "height = [0,1,0,2,1,0,1,3,2,1,2,1]", "output": "6"},
        {"input": "height = [4,2,0,3,2,5]", "output": "9"},
    ],
    "constraints": ["1 <= len(height) <= 2 * 10^4", "0 <= height[i] <= 10^5"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"height": [0, 1, 0, 2, 1, 0, 1, 3]}},
    {"id": "edge", "label": "Slope holds nothing", "input": {"height": [1, 2, 3, 4]}},
    {"id": "worst-case", "label": "Deep basin", "input": {"height": [4, 2, 0, 3, 2, 5]}},
]


def per_column(height):
    total = 0
    for i in range(len(height)):
        #> Water above a column is capped by the tallest bar on each side.
        left = 0
        for j in range(i + 1):
            left = max(left, height[j])
        right = 0
        for j in range(i, len(height)):
            right = max(right, height[j])
        #> The shorter of the two walls decides the level; anything above spills.
        total += min(left, right) - height[i]
    return total


def two_pointers(height):
    lo = 0
    hi = len(height) - 1
    left_max = 0
    right_max = 0
    total = 0
    while lo < hi:
        #> Work on whichever side has the shorter wall. That side's answer is
        #> already decided: a taller wall exists opposite, so its own running max
        #> is what caps the water — we never need to look further.
        if height[lo] < height[hi]:
            left_max = max(left_max, height[lo])
            total += left_max - height[lo]
            lo += 1
        else:
            right_max = max(right_max, height[hi])
            total += right_max - height[hi]
            hi -= 1
    return total


APPROACHES = [
    {"id": "per-column", "label": "Scan both ways per column", "fn": per_column,
     "complexity": {"time": "O(n²)", "space": "O(1)"},
     "viz": {"height": "array", "i": "pointer:height", "j": "pointer:height"}},
    {"id": "two-pointers", "label": "Two pointers", "fn": two_pointers,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"height": "array", "lo": "pointer:height", "hi": "pointer:height"}},
]
