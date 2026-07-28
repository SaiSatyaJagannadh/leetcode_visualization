META = {
    "slug": "3sum",
    "title": "3Sum",
    "pattern": "Two Pointers",
    "difficulty": "Medium",
    "leetcode": 15,
    "prompt": "Find every distinct triple in the array that sums to zero. Two triples with the same three values count as one, whatever their positions.",
    "examples": [
        {"input": "nums = [-1,0,1,2,-1,-4]", "output": "[[-1,-1,2],[-1,0,1]]",
         "why": "Both triples sum to zero; the duplicate -1 does not create a third."},
        {"input": "nums = [0,1,1]", "output": "[]", "why": "No triple reaches zero."},
    ],
    "constraints": ["3 <= len(nums) <= 3000", "No duplicate triples in the answer"],
}

VARIANTS = [
    {"id": "typical", "label": "Two triples", "input": {"nums": [-1, 0, 1, 2, -1, -4]}},
    {"id": "edge", "label": "No answer", "input": {"nums": [0, 1, 1]}},
    {"id": "worst-case", "label": "All zeros", "input": {"nums": [0, 0, 0, 0]}},
]


def sort_and_sweep(nums):
    #> Sorting does double duty: it lets the inner search use two pointers, and it
    #> puts equal values side by side so duplicates are easy to skip.
    ordered = sorted(nums)
    out = []
    for i in range(len(ordered) - 2):
        #> Skip a repeated anchor — it would rebuild triples we already recorded.
        if i > 0 and ordered[i] == ordered[i - 1]:
            continue
        lo = i + 1
        hi = len(ordered) - 1
        while lo < hi:
            total = ordered[i] + ordered[lo] + ordered[hi]
            if total < 0:
                lo += 1  #> Too small; the only way up is to raise the low end.
            elif total > 0:
                hi -= 1  #> Too large; lower the high end.
            else:
                out.append([ordered[i], ordered[lo], ordered[hi]])
                #> Walk both ends past their duplicates so the same triple can't
                #> be recorded twice before the pointers cross.
                while lo < hi and ordered[lo] == ordered[lo + 1]:
                    lo += 1
                while lo < hi and ordered[hi] == ordered[hi - 1]:
                    hi -= 1
                lo += 1
                hi -= 1
    return out


APPROACHES = [
    {"id": "sort-sweep", "label": "Sort, then two pointers", "fn": sort_and_sweep,
     "complexity": {"time": "O(n²)", "space": "O(n)"},
     "viz": {"ordered": "array", "i": "pointer:ordered", "lo": "pointer:ordered", "hi": "pointer:ordered"}},
]
