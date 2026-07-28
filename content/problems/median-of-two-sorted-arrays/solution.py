META = {
    "slug": "median-of-two-sorted-arrays",
    "title": "Median of Two Sorted Arrays",
    "pattern": "Binary Search",
    "difficulty": "Hard",
    "leetcode": 4,
    "prompt": "Two sorted arrays are given. Find the median of the combined sequence without actually merging them, in logarithmic time.",
    "examples": [
        {"input": "nums1 = [1,3], nums2 = [2]", "output": "2.0"},
        {"input": "nums1 = [1,2], nums2 = [3,4]", "output": "2.5", "why": "The middle two are 2 and 3."},
    ],
    "constraints": ["0 <= len(nums1), len(nums2) <= 1000", "Must run in O(log(m+n))"],
}

VARIANTS = [
    {"id": "typical", "label": "Odd total", "input": {"a": [1, 3], "b": [2]}},
    {"id": "edge", "label": "Even total", "input": {"a": [1, 2], "b": [3, 4]}},
    {"id": "worst-case", "label": "No overlap", "input": {"a": [1, 2, 3], "b": [7, 8, 9]}},
]

BIG = 10 ** 9


def merge_then_pick(a, b):
    #> Merging is easy to follow but touches every element.
    merged = []
    i = j = 0
    while i < len(a) or j < len(b):
        if j >= len(b) or (i < len(a) and a[i] <= b[j]):
            merged.append(a[i])
            i += 1
        else:
            merged.append(b[j])
            j += 1
    mid = len(merged) // 2
    if len(merged) % 2 == 1:
        return merged[mid] * 1.0
    return (merged[mid - 1] + merged[mid]) / 2.0


def partition_search(a, b):
    #> Always binary-search the shorter array so the index range stays small.
    if len(a) > len(b):
        a, b = b, a
    total = len(a) + len(b)
    half = (total + 1) // 2
    lo, hi = 0, len(a)
    while True:
        #> Cut a after i elements and b after j, so the left side holds half.
        i = (lo + hi) // 2
        j = half - i
        left_a = a[i - 1] if i > 0 else -BIG
        right_a = a[i] if i < len(a) else BIG
        left_b = b[j - 1] if j > 0 else -BIG
        right_b = b[j] if j < len(b) else BIG
        if left_a <= right_b and left_b <= right_a:
            #> Both cuts agree: everything left is <= everything right, so the
            #> median sits right at the seam. No merge was ever needed.
            if total % 2 == 1:
                return max(left_a, left_b) * 1.0
            return (max(left_a, left_b) + min(right_a, right_b)) / 2.0
        if left_a > right_b:
            hi = i - 1  #> Took too much from a.
        else:
            lo = i + 1  #> Took too little from a.


APPROACHES = [
    {"id": "merge", "label": "Merge then pick", "fn": merge_then_pick,
     "complexity": {"time": "O(m + n)", "space": "O(m + n)"},
     "viz": {"a": "array", "b": "array", "merged": "array", "i": "pointer:a", "j": "pointer:b"}},
    {"id": "partition", "label": "Binary search the cut", "fn": partition_search,
     "complexity": {"time": "O(log min(m,n))", "space": "O(1)"},
     "viz": {"a": "array", "b": "array", "i": "pointer:a", "j": "pointer:b"}},
]
