META = {
    "slug": "daily-temperatures",
    "title": "Daily Temperatures",
    "pattern": "Stack",
    "difficulty": "Medium",
    "leetcode": 739,
    "prompt": "For each day, how many days must you wait for a warmer temperature? Put 0 where no warmer day ever comes.",
    "examples": [
        {"input": "temperatures = [73,74,75,71,69,72,76,73]", "output": "[1,1,4,2,1,1,0,0]"},
        {"input": "temperatures = [30,60,90]", "output": "[1,1,0]"},
    ],
    "constraints": ["1 <= len(temperatures) <= 10^5", "30 <= temperature <= 100"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"temps": [73, 74, 75, 71, 69, 72, 76]}},
    {"id": "edge", "label": "Never warmer", "input": {"temps": [90, 80, 70]}},
    {"id": "worst-case", "label": "Warmer only at the end", "input": {"temps": [70, 69, 68, 67, 99]}},
]


def brute_force(temps):
    out = [0] * len(temps)
    for i in range(len(temps)):
        for j in range(i + 1, len(temps)):
            #> Scan forward until something beats today.
            if temps[j] > temps[i]:
                out[i] = j - i
                break
    return out


def monotonic_stack(temps):
    out = [0] * len(temps)
    #> The stack holds days still waiting for a warmer one, coldest-last. A day
    #> can only be waiting if every day since has been colder, which is exactly
    #> the decreasing order the stack maintains.
    stack = []
    for i in range(len(temps)):
        while stack and temps[i] > temps[stack[-1]]:
            #> Today beats the day on top, so that day's wait ends right now.
            day = stack.pop()
            out[day] = i - day
        stack.append(i)
    #> Anything still stacked never got a warmer day, and 0 is already there.
    return out


APPROACHES = [
    {"id": "brute-force", "label": "Scan forward", "fn": brute_force,
     "complexity": {"time": "O(n²)", "space": "O(1)"},
     "viz": {"temps": "array", "out": "array", "i": "pointer:temps", "j": "pointer:temps"}},
    {"id": "stack", "label": "Monotonic stack", "fn": monotonic_stack,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"temps": "array", "out": "array", "stack": "stack", "i": "pointer:temps"}},
]
