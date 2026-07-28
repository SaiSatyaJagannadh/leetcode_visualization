META = {
    "slug": "letter-combinations-of-a-phone-number",
    "title": "Letter Combinations of a Phone Number",
    "pattern": "Backtracking",
    "difficulty": "Medium",
    "leetcode": 17,
    "prompt": "On a phone keypad each digit from 2 to 9 maps to several letters. Given a string of digits, list every letter combination it could spell.",
    "examples": [
        {"input": 'digits = "23"', "output": '["ad","ae","af","bd","be","bf","cd","ce","cf"]'},
        {"input": 'digits = ""', "output": "[]"},
    ],
    "constraints": ["0 <= len(digits) <= 4", "Digits are 2 through 9"],
    "unordered": True,
}

VARIANTS = [
    {"id": "typical", "label": "Two digits", "input": {"digits": "23"}},
    {"id": "edge", "label": "Empty", "input": {"digits": ""}},
    {"id": "worst-case", "label": "Four-letter key", "input": {"digits": "79"}},
]

KEYS = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}


def backtrack(digits, i=0, current="", out=None):
    if out is None:
        out = []
    if digits == "":
        #> No digits means no combinations, not one empty combination.
        return out
    if i == len(digits):
        out.append(current)
        return out
    for ch in KEYS[digits[i]]:
        #> One level of the tree per digit, one branch per letter on that key.
        backtrack(digits, i + 1, current + ch, out)
    return out


APPROACHES = [
    {"id": "backtrack", "label": "One level per digit", "fn": backtrack,
     "complexity": {"time": "O(4ⁿ)", "space": "O(n)"},
     "viz": {"out": "queue", "$calls": "recursion"}},
]
