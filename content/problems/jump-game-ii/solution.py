META = {
    "slug": "jump-game-ii",
    "title": "Jump Game II",
    "pattern": "Greedy",
    "difficulty": "Medium",
    "leetcode": 45,
    "prompt": "The last index is always reachable. Return the fewest jumps needed to get there from index 0.",
    "examples": [
        {"input": "nums = [2,3,1,1,4]", "output": "2", "why": "Jump to index 1, then to the end."},
        {"input": "nums = [2,3,0,1,4]", "output": "2"},
    ],
    "constraints": ["1 <= len(nums) <= 10^4", "The end is always reachable"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"nums": [2, 3, 1, 1, 4]}},
    {"id": "edge", "label": "Single element", "input": {"nums": [0]}},
    {"id": "worst-case", "label": "One step at a time", "input": {"nums": [1, 1, 1, 1]}},
]


def level_by_level(nums):
    #> This is BFS in disguise: everything reachable in one jump is a level,
    #> everything reachable in two is the next, and so on.
    jumps = 0
    edge = 0  #> Where the current level ends.
    furthest = 0  #> Furthest anything in the current level can reach.
    for i in range(len(nums) - 1):
        if i + nums[i] > furthest:
            furthest = i + nums[i]
        if i == edge:
            #> Ran out of the current level, so a jump is unavoidable here.
            jumps += 1
            edge = furthest
    return jumps


APPROACHES = [
    {"id": "levels", "label": "One jump per level", "fn": level_by_level,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"nums": "array", "i": "pointer:nums", "edge": "pointer:nums", "furthest": "pointer:nums"}},
]
