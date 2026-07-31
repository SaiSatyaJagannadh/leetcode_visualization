META = {
    "slug": "house-robber",
    "title": "House Robber",
    "pattern": "1-D Dynamic Programming",
    "difficulty": "Medium",
    "leetcode": 198,
    "prompt": "Each house holds some money, but robbing two adjacent houses trips the alarm. Return the most you can take.",
    "examples": [
        {"input": "nums = [1,2,3,1]", "output": "4", "why": "Houses 0 and 2."},
        {"input": "nums = [2,7,9,3,1]", "output": "12", "why": "Houses 0, 2 and 4."},
    ],
    "constraints": ["1 <= len(nums) <= 100", "0 <= nums[i] <= 400"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"nums": [2, 7, 9, 3, 1]}},
    {"id": "edge", "label": "One house", "input": {"nums": [5]}},
    {"id": "worst-case", "label": "Skip the big one", "input": {"nums": [2, 1, 1, 9]}},
]


def rolling(nums):
    #> Two running totals: the best if we've just robbed the previous house, and
    #> the best if we skipped it. Nothing older than that ever matters.
    take = 0
    skip = 0
    for n in nums:
        #> Robbing this house means we must have skipped the last one.
        new_take = skip + n
        #> Skipping means we keep the better of the two previous outcomes.
        skip = max(skip, take)
        take = new_take
    return max(take, skip)


def table(nums):
    #> best[i] is the most money obtainable from the first i houses. Writing the
    #> whole table down first makes the recurrence visible; the rolling version
    #> is this same table with everything older than two slots thrown away.
    best = [0] * (len(nums) + 1)
    best[1] = nums[0]
    for i in range(2, len(nums) + 1):
        #> Rob this house and add what was safe two back, or skip it and keep
        #> the previous total. Whichever is larger.
        rob = best[i - 2] + nums[i - 1]
        if rob > best[i - 1]:
            best[i] = rob
        else:
            best[i] = best[i - 1]
    return best[len(nums)]


APPROACHES = [
    {"id": "table", "label": "Full DP table", "fn": table,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"nums": "array", "best": "array", "i": "pointer:best"}},
    {"id": "rolling", "label": "Two rolling totals", "fn": rolling,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"nums": "array"}},
]
