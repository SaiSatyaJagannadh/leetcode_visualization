META = {
    "slug": "two-sum-ii",
    "title": "Two Sum II",
    "pattern": "Two Pointers",
    "difficulty": "Medium",
    "leetcode": 167,
    "prompt": "The array is sorted ascending. Return the 1-based positions of the two numbers adding to the target. Exactly one answer exists and you may use only constant extra space.",
    "examples": [
        {"input": "numbers = [2,7,11,15], target = 9", "output": "[1,2]"},
        {"input": "numbers = [2,3,4], target = 6", "output": "[1,3]"},
    ],
    "constraints": ["2 <= len(numbers) <= 3 * 10^4", "numbers is sorted ascending"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"numbers": [2, 7, 11, 15], "target": 9}},
    {"id": "edge", "label": "Two elements", "input": {"numbers": [1, 4], "target": 5}},
    {"id": "worst-case", "label": "Ends meet in the middle", "input": {"numbers": [1, 3, 4, 6, 8, 11], "target": 10}},
]


def brute_force(numbers, target):
    for i in range(len(numbers)):
        #> Anchor on one number and try every partner to its right.
        for j in range(i + 1, len(numbers)):
            if numbers[i] + numbers[j] == target:
                #> Found it — but note this never once used the fact that the
                #> array is sorted, which is the whole point of the problem.
                return [i + 1, j + 1]
    return []


def two_pointers(numbers, target):
    lo = 0
    hi = len(numbers) - 1
    while lo < hi:
        total = numbers[lo] + numbers[hi]
        if total == target:
            #> Positions are 1-based in this problem, hence the +1.
            return [lo + 1, hi + 1]
        if total < target:
            #> Too small. Since the array is sorted, the only way to gain is to
            #> raise the small end — lowering the big end would lose even more.
            lo += 1
        else:
            #> Too large, so shrink from the big end for the mirror-image reason.
            hi -= 1
    return []


APPROACHES = [
    {"id": "brute-force", "label": "Every pair", "fn": brute_force,
     "complexity": {"time": "O(n²)", "space": "O(1)"},
     "viz": {"numbers": "array", "i": "pointer:numbers", "j": "pointer:numbers"}},
    {"id": "two-pointers", "label": "Two pointers", "fn": two_pointers,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"numbers": "array", "lo": "pointer:numbers", "hi": "pointer:numbers"}},
]
