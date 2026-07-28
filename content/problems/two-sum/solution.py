META = {
    "slug": "two-sum",
    "title": "Two Sum",
    "pattern": "Hash Map",
    "difficulty": "Easy",
    "leetcode": 1,
    "prompt": (
        "Given an array of integers and a target, return the indices of the two "
        "numbers that add up to the target. Exactly one solution exists, and you "
        "may not use the same element twice."
    ),
    "examples": [
        {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]",
         "why": "nums[0] + nums[1] is 2 + 7, which is 9."},
        {"input": "nums = [3,3], target = 6", "output": "[0,1]",
         "why": "Equal values are fine — they are different positions."},
    ],
    "constraints": [
        "2 <= len(nums) <= 10^4",
        "Exactly one valid answer exists.",
    ],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"nums": [2, 7, 11, 15], "target": 9}},
    {"id": "edge", "label": "Duplicates", "input": {"nums": [3, 3], "target": 6}},
    {
        "id": "worst-case",
        "label": "Answer last",
        "input": {"nums": [8, 1, 4, 6, 5, 2, 9], "target": 11},
    },
]


def brute_force(nums, target):
    #> Anchor on one index and try every partner to its right.
    for i in range(len(nums)):
        #> j only walks forward, so no pair is checked twice.
        for j in range(i + 1, len(nums)):
            total = nums[i] + nums[j]  #> Add the pair and compare against the target.
            if total == target:
                #> Found it. Every earlier pair was already ruled out.
                return [i, j]
    return []


def hash_map(nums, target):
    seen = {}  #> seen maps a value we've already passed to the index it sat at.
    for i in range(len(nums)):
        need = target - nums[i]  #> The exact partner this number is waiting for.
        if need in seen:
            #> That partner is behind us, so the pair is complete in one pass.
            return [seen[need], i]
        #> No match yet: remember this number so a later one can find it.
        seen[nums[i]] = i
    return []


APPROACHES = [
    {
        "id": "brute-force",
        "label": "Brute force",
        "fn": brute_force,
        "complexity": {"time": "O(n²)", "space": "O(1)"},
        "viz": {"i": "pointer:nums", "j": "pointer:nums"},
    },
    {
        "id": "hash-map",
        "label": "Hash map",
        "fn": hash_map,
        "complexity": {"time": "O(n)", "space": "O(n)"},
        "viz": {"i": "pointer:nums"},
    },
]
