META = {
    "slug": "detect-squares",
    "title": "Detect Squares",
    "pattern": "Math & Geometry",
    "difficulty": "Medium",
    "leetcode": 2013,
    "prompt": "Points are added over time. Given a query point, count the axis-aligned squares that can be formed using it and three added points.",
    "examples": [
        {"input": "add (0,0),(2,2),(0,2), then count (2,0)", "output": "1"},
        {"input": "count (4,4)", "output": "0"},
    ],
    "constraints": ["At most 5000 calls", "Points may repeat"],
}

PTS = [[0, 0], [2, 2], [0, 2]]

VARIANTS = [
    {"id": "typical", "label": "One square", "input": {"points": [p[:] for p in PTS], "query": [2, 0]}},
    {"id": "edge", "label": "No square", "input": {"points": [p[:] for p in PTS], "query": [4, 4]}},
    {"id": "worst-case", "label": "Duplicate points", "input": {"points": [[0, 0], [0, 0], [2, 2], [0, 2]], "query": [2, 0]}},
]


def count_squares(points, query):
    counts = {}
    for p in points:
        key = str(p[0]) + "," + str(p[1])
        counts[key] = counts.get(key, 0) + 1

    qx, qy = query[0], query[1]
    total = 0
    for key in counts:
        parts = key.split(",")
        px, py = int(parts[0]), int(parts[1])
        #> Only a point diagonally opposite can anchor a square, and for an
        #> axis-aligned square that means equal horizontal and vertical distance.
        if abs(px - qx) != abs(py - qy) or px == qx:
            continue
        #> The diagonal fixes the other two corners exactly, so they just need
        #> looking up. Multiplying the three counts handles duplicate points.
        c1 = counts.get(str(px) + "," + str(qy), 0)
        c2 = counts.get(str(qx) + "," + str(py), 0)
        total += counts[key] * c1 * c2
    return total


APPROACHES = [
    {"id": "diagonal", "label": "Anchor on the opposite corner", "fn": count_squares,
     "complexity": {"time": "O(n) per query", "space": "O(n)"},
     "viz": {"counts": "map", "points": "array"}},
]
