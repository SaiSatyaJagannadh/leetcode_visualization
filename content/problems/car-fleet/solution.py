META = {
    "slug": "car-fleet",
    "title": "Car Fleet",
    "pattern": "Stack",
    "difficulty": "Medium",
    "leetcode": 853,
    "prompt": "Cars drive toward a target at their own speeds. A faster car that catches a slower one is stuck behind it, and they travel on as one fleet. Count the fleets that reach the target.",
    "examples": [
        {"input": "target = 12, position = [10,8,0,5,3], speed = [2,4,1,1,3]", "output": "3"},
        {"input": "target = 10, position = [3], speed = [3]", "output": "1"},
    ],
    "constraints": ["1 <= len(position) <= 10^5", "All positions are distinct"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"target": 12, "position": [10, 8, 0, 5, 3], "speed": [2, 4, 1, 1, 3]}},
    {"id": "edge", "label": "One car", "input": {"target": 10, "position": [3], "speed": [3]}},
    {"id": "worst-case", "label": "All merge into one", "input": {"target": 10, "position": [0, 2, 4], "speed": [1, 1, 1]}},
]


def stack_from_the_front(target, position, speed):
    #> Sort by position descending, so we consider the car nearest the target first.
    cars = sorted(range(len(position)), key=lambda i: -position[i])
    #> times[-1] is the arrival time of the fleet currently in front.
    times = []
    for i in cars:
        #> How long this car would take if the road were empty.
        t = (target - position[i]) / speed[i]
        if times and t <= times[-1]:
            #> It arrives no later than the fleet ahead, which means it catches up
            #> and is absorbed. The fleet's time is set by its slowest car — the
            #> one already on the stack — so we simply drop this car.
            continue
        #> Slower than everything ahead, so it starts a fleet of its own.
        times.append(t)
    return len(times)


APPROACHES = [
    {"id": "stack", "label": "Stack from the front", "fn": stack_from_the_front,
     "complexity": {"time": "O(n log n)", "space": "O(n)"},
     "viz": {"position": "array", "speed": "array", "times": "stack", "cars": "array"}},
]
