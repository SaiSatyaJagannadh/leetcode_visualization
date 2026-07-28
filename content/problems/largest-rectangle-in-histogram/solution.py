META = {
    "slug": "largest-rectangle-in-histogram",
    "title": "Largest Rectangle in Histogram",
    "pattern": "Stack",
    "difficulty": "Hard",
    "leetcode": 84,
    "prompt": "Each number is the height of a bar one unit wide. Find the area of the largest rectangle that fits entirely inside the histogram.",
    "examples": [
        {"input": "heights = [2,1,5,6,2,3]", "output": "10", "why": "The bars of height 5 and 6 give 5 x 2."},
        {"input": "heights = [2,4]", "output": "4"},
    ],
    "constraints": ["1 <= len(heights) <= 10^5", "0 <= heights[i] <= 10^4"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"heights": [2, 1, 5, 6, 2, 3]}},
    {"id": "edge", "label": "Ascending", "input": {"heights": [1, 2, 3]}},
    {"id": "worst-case", "label": "Tall middle", "input": {"heights": [2, 7, 7, 2]}},
]


def brute_force(heights):
    best = 0
    for i in range(len(heights)):
        #> Treat each bar as the shortest in the rectangle and spread outward.
        low = heights[i]
        for j in range(i, len(heights)):
            low = min(low, heights[j])
            best = max(best, low * (j - i + 1))
    return best


def monotonic_stack(heights):
    #> The stack keeps bars in increasing height. A bar stays only while it could
    #> still extend rightward; the moment a shorter bar appears, its run is over.
    stack = []
    best = 0
    for i in range(len(heights) + 1):
        h = 0 if i == len(heights) else heights[i]
        while stack and heights[stack[-1]] >= h:
            #> This bar can't continue past i. Its rectangle spans from just after
            #> whatever is below it on the stack, to just before i.
            top = stack.pop()
            left = stack[-1] + 1 if stack else 0
            best = max(best, heights[top] * (i - left))
        stack.append(i)
    return best


APPROACHES = [
    {"id": "brute-force", "label": "Expand from each bar", "fn": brute_force,
     "complexity": {"time": "O(n²)", "space": "O(1)"},
     "viz": {"heights": "array", "i": "pointer:heights", "j": "pointer:heights"}},
    {"id": "stack", "label": "Monotonic stack", "fn": monotonic_stack,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"heights": "array", "stack": "stack", "i": "pointer:heights"}},
]
