META = {
    "slug": "coin-change",
    "title": "Coin Change",
    "pattern": "1-D Dynamic Programming",
    "difficulty": "Medium",
    "leetcode": 322,
    "prompt": "Given coin denominations and a target amount, return the fewest coins that make the amount exactly, or -1 if it can't be made. You have unlimited coins of each kind.",
    "examples": [
        {"input": "coins = [1,2,5], amount = 11", "output": "3", "why": "5 + 5 + 1."},
        {"input": "coins = [2], amount = 3", "output": "-1"},
    ],
    "constraints": ["1 <= len(coins) <= 12", "0 <= amount <= 10^4"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"coins": [1, 2, 5], "amount": 11}},
    {"id": "edge", "label": "Impossible", "input": {"coins": [2], "amount": 3}},
    {"id": "worst-case", "label": "Greedy would fail", "input": {"coins": [1, 3, 4], "amount": 6}},
]

BIG = 10 ** 9


def bottom_up(coins, amount):
    #> best[a] is the fewest coins making exactly a. BIG marks "not yet possible".
    best = [BIG] * (amount + 1)
    best[0] = 0  #> Zero needs no coins, which seeds everything else.
    for a in range(1, amount + 1):
        for c in coins:
            #> Taking coin c leaves a - c to make, already solved on an earlier
            #> pass. Trying every coin is why greedy failures don't matter here:
            #> for coins [1,3,4] and amount 6, greedy takes 4+1+1 but this finds 3+3.
            if c <= a and best[a - c] + 1 < best[a]:
                best[a] = best[a - c] + 1
    return -1 if best[amount] == BIG else best[amount]


MEMO = {}


def top_down(coins, amount):
    MEMO.clear()
    got = _fewest(coins, amount)
    return -1 if got >= BIG else got


def _fewest(coins, amount):
    #> Nothing left to make, so nothing left to spend.
    if amount == 0:
        return 0
    if amount < 0:
        return BIG
    if amount in MEMO:
        #> Already solved this amount on another branch. Without this line the
        #> same subproblem is recomputed down every path and the tree explodes.
        return MEMO[amount]
    best = BIG
    for c in coins:
        #> Commit to one coin and ask the same question about what remains.
        got = _fewest(coins, amount - c)
        if got + 1 < best:
            best = got + 1
    MEMO[amount] = best
    return best


APPROACHES = [
    {"id": "top-down", "label": "Recursion with a memo", "fn": top_down,
     "complexity": {"time": "O(amount \u00b7 coins)", "space": "O(amount)"},
     "viz": {"coins": "array", "MEMO": "map", "$calls": "recursion"}},
    {"id": "bottom-up", "label": "Build every amount upward", "fn": bottom_up,
     "complexity": {"time": "O(amount · coins)", "space": "O(amount)"},
     "viz": {"coins": "array", "best": "array", "a": "pointer:best"}},
]
