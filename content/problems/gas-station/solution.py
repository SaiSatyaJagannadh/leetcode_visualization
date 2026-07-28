META = {
    "slug": "gas-station",
    "title": "Gas Station",
    "pattern": "Greedy",
    "difficulty": "Medium",
    "leetcode": 134,
    "prompt": "Stations sit in a circle. Each offers some fuel and costs some to leave. Return the index you must start from to complete the loop, or -1 if it's impossible.",
    "examples": [
        {"input": "gas = [1,2,3,4,5], cost = [3,4,5,1,2]", "output": "3"},
        {"input": "gas = [2,3,4], cost = [3,4,3]", "output": "-1"},
    ],
    "constraints": ["1 <= len(gas) <= 10^5", "The answer is unique when it exists"],
}

VARIANTS = [
    {"id": "typical", "label": "Solvable", "input": {"gas": [1, 2, 3, 4, 5], "cost": [3, 4, 5, 1, 2]}},
    {"id": "edge", "label": "Impossible", "input": {"gas": [2, 3, 4], "cost": [3, 4, 3]}},
    {"id": "worst-case", "label": "Start at zero", "input": {"gas": [5, 1, 2], "cost": [1, 2, 5]}},
]


def single_pass(gas, cost):
    total = 0
    tank = 0
    start = 0
    for i in range(len(gas)):
        gain = gas[i] - cost[i]
        total += gain
        tank += gain
        if tank < 0:
            #> Running dry here means no station from `start` up to i could have
            #> worked either — each of them left even less in the tank. So skip
            #> all of them at once and restart after i.
            start = i + 1
            tank = 0
    #> If the whole circuit produces less fuel than it consumes, nothing works.
    return start if total >= 0 else -1


APPROACHES = [
    {"id": "single-pass", "label": "Restart where the tank empties", "fn": single_pass,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"gas": "array", "cost": "array", "i": "pointer:gas", "start": "pointer:gas"}},
]
