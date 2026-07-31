META = {
    "slug": "buy-and-sell-stock-with-cooldown",
    "title": "Buy and Sell Stock With Cooldown",
    "pattern": "2-D Dynamic Programming",
    "difficulty": "Medium",
    "leetcode": 309,
    "prompt": "Buy and sell as often as you like, but after selling you must sit out one day before buying again. Return the largest profit.",
    "examples": [
        {"input": "prices = [1,2,3,0,2]", "output": "3", "why": "Buy 1, sell 2, cool down, buy 0, sell 2."},
        {"input": "prices = [1]", "output": "0"},
    ],
    "constraints": ["1 <= len(prices) <= 5000"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"prices": [1, 2, 3, 0, 2]}},
    {"id": "edge", "label": "Single day", "input": {"prices": [1]}},
    {"id": "worst-case", "label": "Only falls", "input": {"prices": [5, 4, 3]}},
]

BIG = 10 ** 9


def three_states(prices):
    #> Each day you are in one of three situations, and the cooldown rule is just
    #> an edge missing between two of them.
    holding = -prices[0]  #> Own a share.
    cooling = -BIG  #> Sold today, so tomorrow is forbidden.
    free = 0  #> Own nothing and may buy.
    for i in range(1, len(prices)):
        p = prices[i]
        #> Buying is only legal from `free` — never from `cooling`. That single
        #> restriction is the entire cooldown rule.
        new_holding = max(holding, free - p)
        new_cooling = holding + p  #> Selling today puts us in cooldown.
        new_free = max(free, cooling)  #> Yesterday's cooldown expires into free.
        holding, cooling, free = new_holding, new_cooling, new_free
    #> Ending while still holding a share is never better than having sold.
    return max(cooling, free)


CACHE = {}


def decide_each_day(prices):
    #> The same rules asked as a decision tree: on day i, holding or not, what is
    #> the best from here on? The memo collapses the repeated subtrees that the
    #> three-state scan never creates in the first place.
    CACHE.clear()
    return _best(prices, 0, 0)


def _best(prices, i, holding):
    if i >= len(prices):
        #> Out of days. Anything still held is worth nothing.
        return 0
    key = str(i) + ":" + str(holding)
    if key in CACHE:
        return CACHE[key]
    #> Doing nothing is always allowed.
    out = _best(prices, i + 1, holding)
    if holding:
        #> Selling skips the next day entirely — that jump IS the cooldown.
        out = max(out, prices[i] + _best(prices, i + 2, 0))
    else:
        out = max(out, -prices[i] + _best(prices, i + 1, 1))
    CACHE[key] = out
    return out


APPROACHES = [
    {"id": "decision-tree", "label": "Decide each day, memoised", "fn": decide_each_day,
     "complexity": {"time": "O(n)", "space": "O(n)"},
     "viz": {"prices": "array", "CACHE": "map", "$calls": "recursion"}},
    {"id": "states", "label": "Three running states", "fn": three_states,
     "complexity": {"time": "O(n)", "space": "O(1)"},
     "viz": {"prices": "array", "i": "pointer:prices"}},
]
