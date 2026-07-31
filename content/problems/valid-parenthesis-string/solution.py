META = {
    "slug": "valid-parenthesis-string",
    "title": "Valid Parenthesis String",
    "pattern": "Greedy",
    "difficulty": "Medium",
    "leetcode": 678,
    "prompt": "A string holds brackets and stars, where each star may stand for an open bracket, a close bracket, or nothing. Decide whether the string can be read as balanced.",
    "examples": [
        {"input": 's = "(*)"', "output": "true"},
        {"input": 's = "(*))"', "output": "true"},
        {"input": 's = ")("', "output": "false"},
    ],
    "constraints": ["1 <= len(s) <= 100"],
}

VARIANTS = [
    {"id": "typical", "label": "Star as a closer", "input": {"s": "(*))"}},
    {"id": "edge", "label": "Impossible", "input": {"s": ")("}},
    {"id": "worst-case", "label": "Stars as nothing", "input": {"s": "(**)"}},
]


def open_range(s):
    #> Rather than trying every reading of every star, carry the *range* of open
    #> bracket counts that are still possible. Stars widen the range in both
    #> directions at once.
    low = 0
    high = 0
    for ch in s:
        if ch == "(":
            low += 1
            high += 1
        elif ch == ")":
            low -= 1
            high -= 1
        else:
            low -= 1  #> Star read as a closer.
            high += 1  #> Or as an opener.
        if high < 0:
            #> Even the most generous reading has closed too many. Unrecoverable.
            return False
        if low < 0:
            #> Some readings went negative, but those are simply invalid — clamp
            #> rather than fail, because better readings are still alive.
            low = 0
    #> Balanced is possible only if zero open brackets is within reach.
    return low == 0


def two_sweeps(s):
    #> A different proof entirely: sweep left to right treating every star as an
    #> opener, then right to left treating every star as a closer. If neither
    #> sweep ever goes negative, some assignment works.
    count = 0
    for ch in s:
        #> Most generous reading for openers — if this fails, nothing can help.
        if ch == ")":
            count -= 1
        else:
            count += 1
        if count < 0:
            return False
    count = 0
    for i in range(len(s) - 1, -1, -1):
        ch = s[i]
        #> Now the mirror: too many openers is just as fatal seen from the right.
        if ch == "(":
            count -= 1
        else:
            count += 1
        if count < 0:
            return False
    return True


APPROACHES = [
    {"id": "two-sweeps", "label": "Sweep from both ends", "fn": two_sweeps,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"s": "array", "i": "pointer:s"}},
    {"id": "range", "label": "Track the possible range", "fn": open_range,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"s": "array"}},
]
