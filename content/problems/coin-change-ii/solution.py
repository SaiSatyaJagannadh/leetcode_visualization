META = {
    "slug": "coin-change-ii",
    "title": "Coin Change II",
    "pattern": "2-D Dynamic Programming",
    "difficulty": "Medium",
    "leetcode": 518,
    "prompt": "Count the distinct combinations of coins that add up to the amount. Two combinations differing only in order count as one.",
    "examples": [
        {"input": "amount = 5, coins = [1,2,5]", "output": "4"},
        {"input": "amount = 3, coins = [2]", "output": "0"},
    ],
    "constraints": ["1 <= len(coins) <= 300", "0 <= amount <= 5000"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"amount": 5, "coins": [1, 2, 5]}},
    {"id": "edge", "label": "Impossible", "input": {"amount": 3, "coins": [2]}},
    {"id": "worst-case", "label": "Two coins", "input": {"amount": 6, "coins": [2, 3]}},
]


def by_coin(amount, coins):
    ways = [0] * (amount + 1)
    ways[0] = 1  #> One way to make nothing: take no coins.
    for c in coins:
        #> The coin loop being *outside* is what stops order from mattering. Each
        #> coin is fully considered before the next, so 1+2 and 2+1 never both
        #> appear. Swapping the loops would count permutations instead.
        for a in range(c, amount + 1):
            ways[a] += ways[a - c]
    return ways[amount]


CACHE = {}


def by_recursion(amount, coins):
    #> The same count asked top-down: from coin index i, how many ways make a?
    CACHE.clear()
    return _ways(amount, coins, 0)


def _ways(amount, coins, i):
    if amount == 0:
        #> Landed exactly, so the choices made on the way here are one way.
        return 1
    if amount < 0 or i >= len(coins):
        return 0
    key = str(i) + ":" + str(amount)
    if key in CACHE:
        return CACHE[key]
    #> Use coin i again, staying at i — this is what makes 1+2 and 2+1 the same
    #> combination rather than two, exactly as the outer coin loop does.
    same = _ways(amount - coins[i], coins, i)
    #> Or retire coin i for good and move on.
    nxt = _ways(amount, coins, i + 1)
    CACHE[key] = same + nxt
    return CACHE[key]


APPROACHES = [
    {"id": "recursive", "label": "Recursion with a memo", "fn": by_recursion,
     "complexity": {"time": "O(amount \u00b7 coins)", "space": "O(amount \u00b7 coins)"},
     "viz": {"coins": "array", "CACHE": "map", "$calls": "recursion"}},
    {"id": "by-coin", "label": "One coin at a time", "fn": by_coin,
     "complexity": {"time": "O(amount · coins)", "space": "O(amount)"},
     "viz": {"coins": "array", "ways": "array", "a": "pointer:ways"}},
]
