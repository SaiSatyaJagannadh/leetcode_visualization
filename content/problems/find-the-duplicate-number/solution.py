META = {
    "slug": "find-the-duplicate-number",
    "title": "Find the Duplicate Number",
    "pattern": "Linked List",
    "difficulty": "Medium",
    "leetcode": 287,
    "prompt": "An array of n+1 integers holds values from 1 to n, so at least one value repeats. Find it without modifying the array and using constant extra space.",
    "examples": [
        {"input": "nums = [1,3,4,2,2]", "output": "2"},
        {"input": "nums = [3,1,3,4,2]", "output": "3"},
    ],
    "constraints": ["Values are between 1 and n", "Read-only array, O(1) space"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"nums": [1, 3, 4, 2, 2]}},
    {"id": "edge", "label": "Repeat at the front", "input": {"nums": [3, 1, 3, 4, 2]}},
    {"id": "worst-case", "label": "Repeated many times", "input": {"nums": [2, 2, 2, 2, 2]}},
]


def counting(nums):
    #> Correct, but the counter is extra space the problem forbids.
    seen = {}
    for v in nums:
        if v in seen:
            return v
        seen[v] = True
    return -1


def floyd(nums):
    #> Read nums as a linked list: index i points to index nums[i]. Because every
    #> value is a valid index and one index is targeted twice, that list must
    #> contain a cycle, and its entrance is the duplicated value.
    slow = nums[0]
    fast = nums[nums[0]]
    while slow != fast:
        slow = nums[slow]  #> One hop.
        fast = nums[nums[fast]]  #> Two hops.
    #> They met somewhere inside the loop. Restarting one runner from the top and
    #> stepping both singly makes them meet exactly at the entrance.
    slow = 0
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow


APPROACHES = [
    {"id": "counting", "label": "Count what you've seen", "fn": counting,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"nums": "array"}},
    {"id": "floyd", "label": "Cycle detection", "fn": floyd,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"nums": "array", "slow": "pointer:nums", "fast": "pointer:nums"}},
]
