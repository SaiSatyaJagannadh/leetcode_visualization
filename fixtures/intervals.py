"""Overlapping, touching, nested and disjoint — every merge case in one input."""

META = {"slug": "_intervals", "title": "Intervals renderer", "pattern": "Fixture"}

VARIANTS = [
    {
        "id": "typical",
        "label": "All four cases",
        "input": {"spans": [[1, 4], [3, 6], [8, 10], [9, 9], [12, 14], [14, 16]]},
    },
    {"id": "edge", "label": "One nested inside", "input": {"spans": [[1, 20], [4, 6]]}},
]


def merge(spans):
    #> Sorting by start is what makes a single left-to-right sweep enough.
    spans = sorted(spans, key=lambda s: s[0])
    out = []
    for span in spans:
        if out and span[0] <= out[-1][1]:
            #> Overlaps or touches the last kept span, so stretch that one instead.
            out[-1] = [out[-1][0], max(out[-1][1], span[1])]
        else:
            out.append([span[0], span[1]])  #> A clear gap, so this starts a new span.
    return out


APPROACHES = [
    {
        "id": "sweep",
        "label": "Sort and sweep",
        "fn": merge,
        "complexity": {"time": "O(n log n)", "space": "O(n)"},
        "viz": {"spans": "intervals", "out": "intervals", "span": "interval"},
    }
]
