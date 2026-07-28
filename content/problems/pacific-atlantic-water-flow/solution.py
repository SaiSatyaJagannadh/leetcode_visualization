META = {
    "slug": "pacific-atlantic-water-flow",
    "title": "Pacific Atlantic Water Flow",
    "pattern": "Graphs",
    "difficulty": "Medium",
    "leetcode": 417,
    "prompt": "Water flows from a cell to any neighbour of equal or lower height. The Pacific touches the top and left edges, the Atlantic the bottom and right. Find every cell that can drain to both.",
    "examples": [
        {"input": "heights = [[1,2,3],[8,9,4],[7,6,5]]", "output": "the border ring and the 9"},
        {"input": "heights = [[1]]", "output": "[[0,0]]", "why": "A single cell touches both oceans."},
    ],
    "constraints": ["1 <= rows, cols <= 200"],
    "unordered": True,
}

A = [[1, 2, 3], [8, 9, 4], [7, 6, 5]]

VARIANTS = [
    {"id": "typical", "label": "Spiral heights", "input": lambda: {"heights": [r[:] for r in A]}},
    {"id": "edge", "label": "Single cell", "input": lambda: {"heights": [[1]]}},
    {"id": "worst-case", "label": "All equal", "input": lambda: {"heights": [[5, 5], [5, 5]]}},
]


def climb_from_each_ocean(heights):
    rows, cols = len(heights), len(heights[0])
    #> Tracing downhill from every cell would repeat enormous amounts of work.
    #> Instead climb *uphill* from each ocean — anything reachable that way is a
    #> cell whose water can flow back down to it.
    pacific = {}
    atlantic = {}
    for r in range(rows):
        _climb(heights, r, 0, pacific)
        _climb(heights, r, cols - 1, atlantic)
    for c in range(cols):
        _climb(heights, 0, c, pacific)
        _climb(heights, rows - 1, c, atlantic)
    out = []
    for key in pacific:
        #> Both sets reached it, so it drains to both oceans.
        if key in atlantic:
            parts = key.split(",")
            out.append([int(parts[0]), int(parts[1])])
    return sorted(out)


def _climb(heights, r, c, seen):
    stack = [[r, c]]
    while stack:
        cell = stack.pop()
        cr, cc = cell[0], cell[1]
        key = str(cr) + "," + str(cc)
        if key in seen:
            continue
        seen[key] = True
        for d in ([1, 0], [-1, 0], [0, 1], [0, -1]):
            nr, nc = cr + d[0], cc + d[1]
            #> Only step to a neighbour at least as high: that is downhill in
            #> reverse, which is the direction water would actually come from.
            if 0 <= nr < len(heights) and 0 <= nc < len(heights[0]):
                if heights[nr][nc] >= heights[cr][cc]:
                    stack.append([nr, nc])


APPROACHES = [
    {"id": "reverse", "label": "Climb inward from each ocean", "fn": climb_from_each_ocean,
     "complexity": {"time": "O(rc)", "space": "O(rc)"},
     "viz": {"heights": "grid", "pacific": "map", "atlantic": "map", "out": "array"}},
]
