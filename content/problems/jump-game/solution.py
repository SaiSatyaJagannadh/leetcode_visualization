META = {
    "slug": "jump-game",
    "title": "Jump Game",
    "pattern": "Greedy",
    "difficulty": "Medium",
    "leetcode": 55,
    "prompt": "Each value is the furthest you may jump from that position. Starting at index 0, decide whether the last index is reachable.",
    "examples": [
        {"input": "nums = [2,3,1,1,4]", "output": "true"},
        {"input": "nums = [3,2,1,0,4]", "output": "false", "why": "The 0 is a trap you cannot jump over."},
    ],
    "constraints": ["1 <= len(nums) <= 10^4"],
}

VARIANTS = [
    {"id": "typical", "label": "Reachable", "input": {"nums": [2, 3, 1, 1, 4]}},
    {"id": "edge", "label": "Blocked by a zero", "input": {"nums": [3, 2, 1, 0, 4]}},
    {"id": "worst-case", "label": "Only just makes it", "input": {"nums": [1, 1, 1, 0]}},
]


def furthest_reach(nums):
    #> Only one number matters: the furthest index reachable so far. Which exact
    #> jumps got us there is irrelevant to whether we can continue.
    reach = 0
    for i in range(len(nums)):
        if i > reach:
            #> This position is past everything reachable, so the run stops short.
            return False
        if i + nums[i] > reach:
            reach = i + nums[i]
    return True


APPROACHES = [
    {"id": "reach", "label": "Track the furthest reach", "fn": furthest_reach,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"nums": "array", "i": "pointer:nums", "reach": "pointer:nums"}},
]
