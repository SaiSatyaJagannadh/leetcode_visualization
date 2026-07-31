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


def every_triple(nums):
    #> Sort first for the same two reasons, minus the two-pointer trick: equal
    #> values sit together, and each triple comes out in a canonical order.
    ordered = sorted(nums)
    out = []
    seen = {}
    for i in range(len(ordered) - 2):
        for j in range(i + 1, len(ordered) - 1):
            for k in range(j + 1, len(ordered)):
                #> Check every combination of three positions. Nothing is skipped,
                #> which is the whole cost: this is O(n^3) where the sweep is O(n^2).
                if ordered[i] + ordered[j] + ordered[k] == 0:
                    key = str(ordered[i]) + "," + str(ordered[j]) + "," + str(ordered[k])
                    if key not in seen:
                        #> Same values can appear at different positions, so the
                        #> triple itself is the key, not the indices.
                        seen[key] = True
                        out.append([ordered[i], ordered[j], ordered[k]])
    return out


APPROACHES = [
    {"id": "brute-force", "label": "Every triple", "fn": every_triple,
     "complexity": {"time": "O(n\u00b3)", "space": "O(n)"},
     "viz": {"ordered": "array", "i": "pointer:ordered", "j": "pointer:ordered", "k": "pointer:ordered"}},
    {"id": "sort-sweep", "label": "Sort, then two pointers", "fn": sort_and_sweep,
     "complexity": {"time": "O(n²)", "space": "O(n)"},
     "viz": {"ordered": "array", "i": "pointer:ordered", "lo": "pointer:ordered", "hi": "pointer:ordered"}},
]
