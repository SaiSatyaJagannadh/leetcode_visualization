META = {
    "slug": "valid-parentheses",
    "title": "Valid Parentheses",
    "pattern": "Stack",
    "difficulty": "Easy",
    "leetcode": 20,
    "prompt": (
        "A string holds only the six bracket characters. Decide whether every "
        "bracket closes the one most recently opened, with nothing left dangling."
    ),
    "examples": [
        {"input": 's = "([{}])"', "output": "true",
         "why": "Each closer matches the innermost bracket still open."},
        {"input": 's = "(]"', "output": "false",
         "why": "The ] tries to close a ( , which is the wrong partner."},
        {"input": 's = "(("', "output": "false", "why": "Two brackets are never closed."},
    ],
    "constraints": ["1 <= len(s) <= 10^4", "s contains only ()[]{} characters"],
}

VARIANTS = [
    {"id": "typical", "label": "Nested", "input": {"s": "([{}])"}},
    {"id": "edge", "label": "Wrong partner", "input": {"s": "(]"}},
    {"id": "worst-case", "label": "Never closed", "input": {"s": "([)]"}},
]

PAIRS = {")": "(", "]": "[", "}": "{"}


def with_stack(s):
    #> The stack remembers openers in the order they'll need closing: newest first.
    stack = []
    for ch in s:
        if ch in PAIRS:
            #> A closer is only valid against the most recent opener.
            if not stack or stack[-1] != PAIRS[ch]:
                return False  #> Mismatch, and no later character can repair it.
            stack.pop()  #> Matched, so the pair cancels out and disappears.
        else:
            stack.append(ch)
    #> Anything still on the stack was opened and never closed.
    return len(stack) == 0


def replace_pairs(s):
    #> Repeatedly delete adjacent matching pairs; a valid string collapses to nothing.
    text = s
    while True:
        shorter = text.replace("()", "").replace("[]", "").replace("{}", "")
        if shorter == text:
            #> Nothing collapsed this round, so whatever is left can never match.
            break
        text = shorter
    return len(text) == 0


APPROACHES = [
    {
        "id": "stack",
        "label": "Stack",
        "fn": with_stack,
        "complexity": {"time": "O(n)", "space": "O(n)"},
        "viz": {"stack": "stack", "s": "array"},
    },
    {
        "id": "collapse",
        "label": "Collapse pairs",
        "fn": replace_pairs,
        "complexity": {"time": "O(n²)", "space": "O(n)"},
        "viz": {"s": "array"},
    },
]
