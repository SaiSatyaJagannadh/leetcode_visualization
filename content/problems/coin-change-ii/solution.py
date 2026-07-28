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


APPROACHES = [
    {"id": "by-coin", "label": "One coin at a time", "fn": by_coin,
     "complexity": {"time": "O(amount · coins)", "space": "O(amount)"},
     "viz": {"coins": "array", "ways": "array", "a": "pointer:ways"}},
]
