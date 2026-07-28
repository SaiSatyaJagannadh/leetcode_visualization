META = {
    "slug": "longest-consecutive-sequence",
    "title": "Longest Consecutive Sequence",
    "pattern": "Arrays & Hashing",
    "difficulty": "Medium",
    "leetcode": 128,
    "prompt": "Find the length of the longest run of consecutive integers present in the array. The numbers may appear in any order, and the run does not have to be contiguous in the array itself.",
    "examples": [
        {"input": "nums = [100,4,200,1,3,2]", "output": "4",
         "why": "1, 2, 3 and 4 are all present, scattered through the array."},
        {"input": "nums = []", "output": "0"},
    ],
    "constraints": ["0 <= len(nums) <= 10^5", "Must run in O(n) time"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"nums": [100, 4, 200, 1, 3, 2]}},
    {"id": "edge", "label": "No run at all", "input": {"nums": [10, 30, 50]}},
    {"id": "worst-case", "label": "Two runs, duplicates", "input": {"nums": [1, 2, 0, 1, 9, 8, 7]}},
]


def sort_then_scan(nums):
    if not nums:
        return 0
    #> Sorting puts a run next to itself, but costs n log n — more than allowed.
    ordered = sorted(nums)
    best = 1
    run = 1
    for i in range(1, len(ordered)):
        if ordered[i] == ordered[i - 1]:
            continue  #> A repeat neither extends nor breaks the run.
        if ordered[i] == ordered[i - 1] + 1:
            run += 1  #> Exactly one more than the last, so the run grows.
            if run > best:
                best = run
        else:
            run = 1  #> A gap. Start counting again from here.
    return best


def from_run_starts(nums):
    #> A set gives O(1) "is this number present", which is the whole engine.
    present = {}
    for v in nums:
        present[v] = True
    best = 0
    for v in present:
        #> Only count from the *start* of a run. If v-1 exists, v is mid-run and
        #> some earlier iteration already walked through it — this single check
        #> is what keeps the whole thing linear instead of quadratic.
        if v - 1 in present:
            continue
        length = 1
        while v + length in present:
            #> Walk forward as far as the run goes.
            length += 1
        if length > best:
            best = length
    return best


APPROACHES = [
    {"id": "sort", "label": "Sort and scan", "fn": sort_then_scan,
     "complexity": {"time": "O(n log n)", "space": "O(n)"},
     "viz": {"nums": "array", "ordered": "array", "i": "pointer:ordered"}},
    {"id": "run-starts", "label": "Only start at run starts", "fn": from_run_starts,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"nums": "array"}},
]
