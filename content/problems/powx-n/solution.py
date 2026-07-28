META = {
    "slug": "powx-n",
    "title": "Pow(x, n)",
    "pattern": "Math & Geometry",
    "difficulty": "Medium",
    "leetcode": 50,
    "prompt": "Raise x to the power n, where n may be negative. Do it in logarithmic time rather than by repeated multiplication.",
    "examples": [
        {"input": "x = 2.0, n = 10", "output": "1024.0"},
        {"input": "x = 2.0, n = -2", "output": "0.25"},
    ],
    "constraints": ["-100 < x < 100", "n fits in a 32-bit integer"],
}

VARIANTS = [
    {"id": "typical", "label": "Positive power", "input": {"x": 2.0, "n": 10}},
    {"id": "edge", "label": "Negative power", "input": {"x": 2.0, "n": -2}},
    {"id": "worst-case", "label": "Zero power", "input": {"x": 3.0, "n": 0}},
]


def fast_power(x, n):
    #> A negative exponent is the reciprocal of the positive one.
    base = x
    power = n
    if power < 0:
        base = 1 / base
        power = -power
    result = 1.0
    while power > 0:
        #> Squaring the base each round means the exponent halves, so the work is
        #> logarithmic. The odd bit is what decides whether to fold in the base.
        if power % 2 == 1:
            result = result * base
        base = base * base
        power = power // 2
    return result


APPROACHES = [
    {"id": "fast", "label": "Square and halve", "fn": fast_power,
     "complexity": {"time": "O(log n)", "space": "O(1)"},
     "viz": {}},
]
