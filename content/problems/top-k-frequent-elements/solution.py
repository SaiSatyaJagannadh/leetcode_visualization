META = {
    "slug": "top-k-frequent-elements",
    "title": "Top K Frequent Elements",
    "pattern": "Arrays & Hashing",
    "difficulty": "Medium",
    "leetcode": 347,
    "prompt": "Return the k values that appear most often in the array. The answer is guaranteed to be unique.",
    "examples": [
        {"input": "nums = [1,1,1,2,2,3], k = 2", "output": "[1,2]",
         "why": "1 appears three times and 2 twice; 3 appears once and misses out."},
        {"input": "nums = [1], k = 1", "output": "[1]"},
    ],
    "constraints": ["1 <= len(nums) <= 10^5", "k is between 1 and the number of distinct values"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"nums": [1, 1, 1, 2, 2, 3], "k": 2}},
    {"id": "edge", "label": "All distinct", "input": {"nums": [5, 6, 7], "k": 1}},
    {"id": "worst-case", "label": "Ties broken by count", "input": {"nums": [4, 4, 5, 5, 6, 4, 5, 7], "k": 2}},
]


def sort_by_count(nums, k):
    counts = {}
    for v in nums:
        counts[v] = counts.get(v, 0) + 1
    #> Sorting every distinct value costs more than we need: only the top k matter.
    ordered = sorted(counts, key=lambda v: -counts[v])
    return ordered[:k]


def bucket_by_count(nums, k):
    counts = {}
    for v in nums:
        counts[v] = counts.get(v, 0) + 1
    #> A value can appear at most len(nums) times, so frequency itself can be an
    #> index. That turns "sort by count" into "read the buckets backwards".
    buckets = [[] for _ in range(len(nums) + 1)]
    for v in counts:
        buckets[counts[v]].append(v)
    out = []
    for freq in range(len(buckets) - 1, 0, -1):
        for v in buckets[freq]:
            #> Walking down from the highest frequency hands them over in order.
            out.append(v)
            if len(out) == k:
                return out
    return out


APPROACHES = [
    {"id": "sort", "label": "Sort by count", "fn": sort_by_count,
     "complexity": {"time": "O(n log n)", "space": "O(n)"},
     "viz": {"nums": "array", "ordered": "array"}},
    {"id": "bucket", "label": "Bucket by count", "fn": bucket_by_count,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"nums": "array", "out": "queue", "freq": "pointer:buckets"}},
]
