META = {
    "slug": "reverse-integer",
    "title": "Reverse Integer",
    "pattern": "Bit Manipulation",
    "difficulty": "Medium",
    "leetcode": 7,
    "prompt": "Reverse the digits of a signed integer. If the result falls outside the signed 32-bit range, return 0.",
    "examples": [
        {"input": "x = 123", "output": "321"},
        {"input": "x = -123", "output": "-321"},
        {"input": "x = 1534236469", "output": "0", "why": "Reversed it overflows 32 bits."},
    ],
    "constraints": ["-2^31 <= x <= 2^31 - 1"],
}

VARIANTS = [
    {"id": "typical", "label": "Positive", "input": {"x": 123}},
    {"id": "edge", "label": "Negative", "input": {"x": -123}},
    {"id": "worst-case", "label": "Overflows", "input": {"x": 1534236469}},
]

LIMIT = 2147483647


def digit_by_digit(x):
    #> Handle the sign separately so the digit loop only deals with a positive
    #> number — trailing zeros and negatives both stop being special cases.
    negative = x < 0
    value = -x if negative else x
    result = 0
    while value > 0:
        digit = value % 10
        value = value // 10
        #> Check before multiplying, not after: in a fixed-width language the
        #> overflow would already have happened by then.
        if result > (LIMIT - digit) // 10:
            return 0
        result = result * 10 + digit
    return -result if negative else result


def via_string(x):
    #> Treat it as text: strip the sign, reverse the characters, read it back.
    #> Short and clear, and it can only be written in a language whose integers
    #> do not overflow — the check has to happen after the fact, not before.
    negative = x < 0
    text = str(-x if negative else x)
    flipped = text[::-1]
    result = int(flipped)
    if result > LIMIT:
        #> Too late in a fixed-width language: `result` already overflowed while
        #> being built. Here the guard still works because Python grew the number.
        return 0
    return -result if negative else result


APPROACHES = [
    {"id": "via-string", "label": "Reverse the characters", "fn": via_string,
     "complexity": {"time": "O(digits)", "space": "O(digits)"},
     "viz": {}},
    {"id": "digits", "label": "Pop digits, check before pushing", "fn": digit_by_digit,
     "complexity": {"time": "O(log x)", "space": "O(1)"},
     "viz": {}},
]
