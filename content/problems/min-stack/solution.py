META = {
    "slug": "min-stack",
    "title": "Min Stack",
    "pattern": "Stack",
    "difficulty": "Medium",
    "leetcode": 155,
    "prompt": "Design a stack that also reports its smallest element, with push, pop, top and getMin all running in constant time. The trace replays a sequence of operations.",
    "examples": [
        {"input": "push(-2), push(0), push(-3), getMin()", "output": "-3"},
        {"input": "pop(), top(), getMin()", "output": "0, then -2",
         "why": "Removing -3 has to restore -2 as the minimum instantly."},
    ],
    "constraints": ["All four operations must be O(1)", "pop and top are never called on an empty stack"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"ops": [-2, 0, -3, "pop", "pop", 5]}},
    {"id": "edge", "label": "Ascending pushes", "input": {"ops": [1, 2, 3, "pop"]}},
    {"id": "worst-case", "label": "New minimum each push", "input": {"ops": [5, 4, 3, 2, "pop", "pop"]}},
]


def paired_stack(ops):
    stack = []
    #> mins[i] is the smallest value anywhere in stack[0..i]. Storing it per level
    #> is what makes getMin O(1) — and makes pop restore the old minimum for free.
    mins = []
    log = []
    for op in ops:
        if op == "pop":
            stack.pop()
            #> Discarding the paired entry rewinds the minimum automatically.
            mins.pop()
        else:
            stack.append(op)
            #> The new minimum is this value, or the old one, whichever is smaller.
            if mins:
                mins.append(min(op, mins[-1]))
            else:
                mins.append(op)
        log.append(mins[-1] if mins else None)
    return log


APPROACHES = [
    {"id": "paired", "label": "Parallel minimum stack", "fn": paired_stack,
     "complexity": {"time": "O(1) per op", "space": "O(n)"},
     "viz": {"stack": "stack", "mins": "stack", "log": "queue", "ops": "array"}},
]
