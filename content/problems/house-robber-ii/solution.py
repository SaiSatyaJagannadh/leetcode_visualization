META = {
    "slug": "house-robber-ii",
    "title": "House Robber II",
    "pattern": "1-D Dynamic Programming",
    "difficulty": "Medium",
    "leetcode": 213,
    "prompt": "Same as House Robber, except the houses form a circle, so the first and last are adjacent too.",
    "examples": [
        {"input": "nums = [2,3,2]", "output": "3", "why": "Robbing 0 and 2 is now forbidden."},
        {"input": "nums = [1,2,3,1]", "output": "4"},
    ],
    "constraints": ["1 <= len(nums) <= 100"],
}

VARIANTS = [
    {"id": "typical", "label": "Circle bites", "input": {"nums": [2, 3, 2]}},
    {"id": "edge", "label": "One house", "input": {"nums": [5]}},
    {"id": "worst-case", "label": "Ends are richest", "input": {"nums": [6, 1, 1, 6]}},
]


def two_passes(nums):
    if len(nums) == 1:
        #> With a single house there is no circle to worry about.
        return nums[0]
    #> The first and last house can't both be robbed, so one of them is out.
    #> Solving the straight-line problem twice — once without each end — covers
    #> every legal choice, and neither run can wrap around.
    without_last = _line(nums[:-1])
    without_first = _line(nums[1:])
    return max(without_last, without_first)


def _line(row):
    take = 0
    skip = 0
    for n in row:
        new_take = skip + n
        skip = max(skip, take)
        take = new_take
    return max(take, skip)


def compare_two_tables(nums):
    #> Same two runs, but with the whole table kept so both answers are visible
    #> side by side instead of collapsing into two numbers.
    if len(nums) == 1:
        return nums[0]
    a = _table(nums[:-1])
    b = _table(nums[1:])
    #> The circle forbids taking both ends, so the answer is whichever line wins.
    return max(a[len(a) - 1], b[len(b) - 1])


def _table(row):
    best = [0] * (len(row) + 1)
    best[1] = row[0]
    for i in range(2, len(row) + 1):
        rob = best[i - 2] + row[i - 1]
        #> Rob this house and add what was safe two back, or keep the running best.
        if rob > best[i - 1]:
            best[i] = rob
        else:
            best[i] = best[i - 1]
    return best


APPROACHES = [
    {"id": "tables", "label": "Both tables side by side", "fn": compare_two_tables,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"nums": "array", "a": "array", "b": "array", "best": "array", "i": "pointer:best"}},
    {"id": "two-passes", "label": "Drop one end, twice", "fn": two_passes,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"nums": "array"}},
]
