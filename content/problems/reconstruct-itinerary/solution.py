META = {
    "slug": "reconstruct-itinerary",
    "title": "Reconstruct Itinerary",
    "pattern": "Advanced Graphs",
    "difficulty": "Hard",
    "leetcode": 332,
    "prompt": "Given a pile of airline tickets, order them into one trip starting at JFK that uses every ticket exactly once. If several trips are possible, return the one that reads smallest alphabetically.",
    "examples": [
        {"input": 'tickets = [["MUC","LHR"],["JFK","MUC"],["SFO","SJC"],["LHR","SFO"]]',
         "output": '["JFK","MUC","LHR","SFO","SJC"]'},
        {"input": 'tickets = [["JFK","KUL"],["JFK","NRT"],["NRT","JFK"]]',
         "output": '["JFK","NRT","JFK","KUL"]',
         "why": "Taking KUL first would strand the trip, so the greedy choice must be undone."},
    ],
    "constraints": ["1 <= number of tickets <= 300", "A valid itinerary always exists"],
}

A = [["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"], ["LHR", "SFO"]]
TRAP = [["JFK", "KUL"], ["JFK", "NRT"], ["NRT", "JFK"]]

VARIANTS = [
    {"id": "typical", "label": "Straight line", "input": lambda: {"tickets": [t[:] for t in A]}},
    {"id": "edge", "label": "Dead end first", "input": lambda: {"tickets": [t[:] for t in TRAP]}},
    {"id": "worst-case", "label": "Return trip", "input": lambda: {"tickets": [["JFK", "A"], ["A", "JFK"], ["JFK", "B"]]}},
]


def hierholzer(tickets):
    #> Sorted destinations means the alphabetically smallest is always taken first.
    routes = {}
    for t in sorted(tickets):
        routes.setdefault(t[0], []).append(t[1])

    #> Hierholzer's: fly greedily until stuck, and whatever airport you're stranded
    #> at must be the *end* of the trip. Push it, back up, and keep going. The
    #> route comes out backwards, which is why it is reversed at the end.
    stack = ["JFK"]
    route = []
    while stack:
        here = stack[-1]
        if routes.get(here):
            #> Still have an unused ticket out, so take the smallest one.
            stack.append(routes[here].pop(0))
        else:
            #> Stranded. This airport is as far as the trip gets from here.
            route.append(stack.pop())
    route.reverse()
    return route


def backtrack_route(tickets):
    #> The direct search: try tickets in alphabetical order and commit, undoing
    #> whenever the trip strands us with tickets unused. The first complete
    #> route found is the smallest, because every choice was made smallest-first.
    routes = {}
    for t in sorted(tickets):
        routes.setdefault(t[0], []).append(t[1])
    route = ["JFK"]
    _fly(routes, "JFK", len(tickets), route)
    return route


def _fly(routes, here, left, route):
    if left == 0:
        #> Every ticket used, so this is a complete trip.
        return True
    options = routes.get(here, [])
    for i in range(len(options)):
        nxt = options[i]
        #> Take this ticket out of circulation before flying on.
        options.pop(i)
        route.append(nxt)
        if _fly(routes, nxt, left - 1, route):
            return True
        #> Dead end: put the ticket back and the airport out of the route.
        options.insert(i, nxt)
        route.pop()
    return False


APPROACHES = [
    {"id": "backtrack", "label": "Try tickets, undo dead ends", "fn": backtrack_route,
     "complexity": {"time": "O(E!)", "space": "O(E)"},
     "viz": {"routes": "map", "route": "queue", "$calls": "recursion"}},
    {"id": "hierholzer", "label": "Fly until stuck, then back up", "fn": hierholzer,
     "complexity": {"time": "O(E log E)", "space": "O(E)"},
     "viz": {"routes": "map", "stack": "stack", "route": "queue"}},
]
