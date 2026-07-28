META = {
    "slug": "container-with-most-water",
    "title": "Container With Most Water",
    "pattern": "Two Pointers",
    "difficulty": "Medium",
    "leetcode": 11,
    "prompt": (
        "Each entry in the array is the height of a vertical line standing on a "
        "number line. Pick two lines so that the water held between them is as "
        "deep as possible. Return that area."
    ),
    "examples": [
        {"input": "height = [1,8,6,2,5,4,8,3,7]", "output": "49",
         "why": "The lines at index 1 and 8 are 7 apart and the shorter is 7, so 7 x 7."},
        {"input": "height = [1,1]", "output": "1",
         "why": "Only one pair exists: width 1, height 1."},
    ],
    "constraints": ["2 <= len(height) <= 10^5", "0 <= height[i] <= 10^4"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"height": [1, 8, 6, 2, 5, 4, 8, 3, 7]}},
    {"id": "edge", "label": "Two bars", "input": {"height": [1, 1]}},
    {"id": "worst-case", "label": "Tallest outside", "input": {"height": [2, 3, 4, 5, 18, 17, 6]}},
]


def brute_force(height):
    best = 0
    for i in range(len(height)):
        for j in range(i + 1, len(height)):
            #> Water spills over the shorter wall, so that one sets the depth.
            depth = min(height[i], height[j])
            area = depth * (j - i)
            if area > best:
                best = area  #> A new record; every pair checked so far was worse.
    return best


def two_pointers(height):
    #> Start as wide as possible: no pair will ever have more width than this.
    lo = 0
    hi = len(height) - 1
    best = 0
    while lo < hi:
        depth = min(height[lo], height[hi])
        area = depth * (hi - lo)
        if area > best:
            best = area
        #> Moving the taller wall inward can only lose width and never gain depth,
        #> so the shorter wall is the only move that can possibly help.
        if height[lo] < height[hi]:
            lo += 1
        else:
            hi -= 1
    return best


APPROACHES = [
    {
        "id": "brute-force",
        "label": "Every pair",
        "fn": brute_force,
        "complexity": {"time": "O(n²)", "space": "O(1)"},
        "viz": {"height": "array", "i": "pointer:height", "j": "pointer:height"},
    },
    {
        "id": "two-pointers",
        "label": "Two pointers",
        "fn": two_pointers,
        "complexity": {"time": "O(n)", "space": "O(1)"},
        "viz": {"height": "array", "lo": "pointer:height", "hi": "pointer:height"},
    },
]
