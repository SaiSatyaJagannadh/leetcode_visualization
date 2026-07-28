META = {
    "slug": "maximum-subarray",
    "title": "Maximum Subarray",
    "pattern": "Greedy",
    "difficulty": "Medium",
    "leetcode": 53,
    "prompt": (
        "Find the contiguous run of numbers with the largest sum and return that "
        "sum. The run must hold at least one number."
    ),
    "examples": [
        {"input": "nums = [-2,1,-3,4,-1,2,1,-5,4]", "output": "6",
         "why": "The run [4,-1,2,1] sums to 6, and nothing beats it."},
        {"input": "nums = [-3,-1,-2]", "output": "-1",
         "why": "All negative, so the best you can do is take the least bad single number."},
    ],
    "constraints": ["1 <= len(nums) <= 10^5", "-10^4 <= nums[i] <= 10^4"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}},
    {"id": "edge", "label": "All negative", "input": {"nums": [-3, -1, -2]}},
    {"id": "worst-case", "label": "Best run last", "input": {"nums": [3, -4, 1, -1, 5, 2]}},
]


def brute_force(nums):
    best = nums[0]
    for i in range(len(nums)):
        total = 0
        for j in range(i, len(nums)):
            #> Extend the run starting at i one number at a time.
            total += nums[j]
            if total > best:
                best = total
    return best


def kadane(nums):
    #> running is the best sum of a run that ends exactly at the current position.
    running = nums[0]
    best = nums[0]
    for i in range(1, len(nums)):
        n = nums[i]
        #> The only real decision: extend the run behind us, or start fresh here.
        #> If what's behind is negative it can only drag us down, so we drop it.
        running = max(n, running + n)
        if running > best:
            #> This run ends better than any run we've finished before.
            best = running
    return best


APPROACHES = [
    {
        "id": "brute-force",
        "label": "Every run",
        "fn": brute_force,
        "complexity": {"time": "O(n²)", "space": "O(1)"},
        "viz": {"nums": "array", "i": "pointer:nums", "j": "pointer:nums"},
    },
    {
        "id": "kadane",
        "label": "Kadane's scan",
        "fn": kadane,
        "complexity": {"time": "O(n)", "space": "O(1)"},
        "viz": {"nums": "array", "i": "pointer:nums"},
    },
]
