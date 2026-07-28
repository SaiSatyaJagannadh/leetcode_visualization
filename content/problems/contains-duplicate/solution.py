META = {
    "slug": "contains-duplicate",
    "title": "Contains Duplicate",
    "pattern": "Arrays & Hashing",
    "difficulty": "Easy",
    "leetcode": 217,
    "prompt": "Return true if any value appears at least twice in the array, and false if every element is distinct.",
    "examples": [
        {"input": "nums = [1,2,3,1]", "output": "true", "why": "1 shows up at both ends."},
        {"input": "nums = [1,2,3,4]", "output": "false", "why": "Every value is distinct."},
    ],
    "constraints": ["1 <= len(nums) <= 10^5", "-10^9 <= nums[i] <= 10^9"],
}

VARIANTS = [
    {"id": "typical", "label": "Has a duplicate", "input": {"nums": [1, 2, 3, 1]}},
    {"id": "edge", "label": "All distinct", "input": {"nums": [1, 2, 3, 4]}},
    {"id": "worst-case", "label": "Duplicate at the end", "input": {"nums": [4, 1, 7, 3, 9, 4]}},
]


def brute_force(nums):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            #> Compare every pair exactly once by keeping j ahead of i.
            if nums[i] == nums[j]:
                return True
    return False


def hash_set(nums):
    #> seen holds every value already walked past.
    seen = {}
    for i in range(len(nums)):
        v = nums[i]
        if v in seen:
            #> Met this value before, so we can answer without reading the rest.
            return True
        #> Record it so a later copy of the same value trips the check above.
        seen[v] = i
    return False


APPROACHES = [
    {"id": "brute-force", "label": "Every pair", "fn": brute_force,
     "complexity": {"time": "O(n²)", "space": "O(1)"},
     "viz": {"nums": "array", "i": "pointer:nums", "j": "pointer:nums"}},
    {"id": "hash-set", "label": "Hash set", "fn": hash_set,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"nums": "array", "i": "pointer:nums"}},
]
