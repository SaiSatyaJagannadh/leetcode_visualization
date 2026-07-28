META = {
    "slug": "evaluate-reverse-polish-notation",
    "title": "Evaluate Reverse Polish Notation",
    "pattern": "Stack",
    "difficulty": "Medium",
    "leetcode": 150,
    "prompt": "Evaluate an arithmetic expression written in postfix form, where each operator follows its two operands. Division truncates toward zero.",
    "examples": [
        {"input": 'tokens = ["2","1","+","3","*"]', "output": "9", "why": "(2 + 1) * 3."},
        {"input": 'tokens = ["4","13","5","/","+"]', "output": "6", "why": "4 + (13 / 5) = 4 + 2."},
    ],
    "constraints": ["1 <= len(tokens) <= 10^4", "The expression is always valid"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"tokens": ["2", "1", "+", "3", "*"]}},
    {"id": "edge", "label": "Single number", "input": {"tokens": ["42"]}},
    {"id": "worst-case", "label": "Truncating division", "input": {"tokens": ["4", "13", "5", "/", "+"]}},
]

OPS = ["+", "-", "*", "/"]


def with_stack(tokens):
    #> Postfix needs no brackets because the stack remembers what is still pending.
    stack = []
    for tok in tokens:
        if tok not in OPS:
            stack.append(int(tok))
            continue
        #> An operator's two operands are always the top two values, and the
        #> second one popped is the left-hand side.
        right = stack.pop()
        left = stack.pop()
        if tok == "+":
            stack.append(left + right)
        elif tok == "-":
            stack.append(left - right)
        elif tok == "*":
            stack.append(left * right)
        else:
            #> int() truncates toward zero; Python's // would floor toward -inf.
            stack.append(int(left / right))
    #> A valid expression leaves exactly one value behind.
    return stack[0]


APPROACHES = [
    {"id": "stack", "label": "Stack", "fn": with_stack,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"stack": "stack", "tokens": "array"}},
]
