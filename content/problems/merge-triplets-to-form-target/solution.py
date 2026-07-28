META = {
    "slug": "merge-triplets-to-form-target",
    "title": "Merge Triplets to Form Target",
    "pattern": "Greedy",
    "difficulty": "Medium",
    "leetcode": 1899,
    "prompt": "Merging two triplets keeps the larger value in each position. Decide whether some sequence of merges can produce the target triplet.",
    "examples": [
        {"input": "triplets = [[2,5,3],[1,8,4],[1,7,5]], target = [2,7,5]", "output": "true"},
        {"input": "triplets = [[3,4,5],[4,5,6]], target = [3,2,5]", "output": "false"},
    ],
    "constraints": ["1 <= len(triplets) <= 10^5"],
}

VARIANTS = [
    {"id": "typical", "label": "Achievable", "input": {"triplets": [[2, 5, 3], [1, 8, 4], [1, 7, 5]], "target": [2, 7, 5]}},
    {"id": "edge", "label": "Impossible", "input": {"triplets": [[3, 4, 5], [4, 5, 6]], "target": [3, 2, 5]}},
    {"id": "worst-case", "label": "Exact match present", "input": {"triplets": [[1, 1, 1], [2, 7, 5]], "target": [2, 7, 5]}},
]


def usable_only(triplets, target):
    #> Merging never lowers a value, so any triplet exceeding the target in any
    #> position poisons the result forever and must be discarded outright.
    best = [0, 0, 0]
    for t in triplets:
        if t[0] > target[0] or t[1] > target[1] or t[2] > target[2]:
            continue
        #> Every surviving triplet is safe to merge in, so merge them all — there
        #> is no downside and therefore no choice to agonise over.
        for i in range(3):
            if t[i] > best[i]:
                best[i] = t[i]
    return best == target


APPROACHES = [
    {"id": "usable", "label": "Merge everything that fits", "fn": usable_only,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"triplets": "array", "best": "array", "target": "array"}},
]
