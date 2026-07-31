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


def halve_recursively(x, n):
    #> The same halving read top-down. x^n is (x^(n/2)) squared, which states the
    #> saving directly: one subproblem, not two, so the depth is log n.
    base = x
    power = n
    if power < 0:
        base = 1 / base
        power = -power
    return _pow(base, power)


def _pow(base, power):
    if power == 0:
        #> Anything to the zero is one, which anchors the whole recursion.
        return 1.0
    half = _pow(base, power // 2)
    if power % 2 == 0:
        #> Even: the two halves are identical, so square the one we computed.
        return half * half
    #> Odd: squaring loses one factor of the base, so put it back.
    return half * half * base


APPROACHES = [
    {"id": "recursive", "label": "Halve recursively", "fn": halve_recursively,
     "complexity": {"time": "O(log n)", "space": "O(log n)"},
     "viz": {"$calls": "recursion"}},
    {"id": "fast", "label": "Square and halve", "fn": fast_power,
     "complexity": {"time": "O(log n)", "space": "O(1)"},
     "viz": {}},
]
