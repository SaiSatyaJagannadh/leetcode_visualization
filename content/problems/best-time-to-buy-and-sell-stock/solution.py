META = {
    "slug": "best-time-to-buy-and-sell-stock",
    "title": "Best Time to Buy and Sell Stock",
    "pattern": "Sliding Window",
    "difficulty": "Easy",
    "leetcode": 121,
    "prompt": (
        "The array holds a stock's price on each day. Buy on one day and sell on a "
        "later day to make the largest profit you can. If no day pair turns a "
        "profit, return 0."
    ),
    "examples": [
        {"input": "prices = [7,1,5,3,6,4]", "output": "5",
         "why": "Buy at 1 on day 1, sell at 6 on day 4."},
        {"input": "prices = [7,6,4,3,1]", "output": "0",
         "why": "Prices only fall, so the best move is not to trade."},
    ],
    "constraints": ["1 <= len(prices) <= 10^5", "0 <= prices[i] <= 10^4"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"prices": [7, 1, 5, 3, 6, 4]}},
    {"id": "edge", "label": "Only falls", "input": {"prices": [7, 6, 4, 3, 1]}},
    {"id": "worst-case", "label": "Best trade last", "input": {"prices": [3, 8, 2, 4, 1, 9]}},
]


def brute_force(prices):
    best = 0
    for buy in range(len(prices)):
        for sell in range(buy + 1, len(prices)):
            #> Selling before buying isn't allowed, so sell always starts after buy.
            profit = prices[sell] - prices[buy]
            if profit > best:
                best = profit
    return best


def one_pass(prices):
    #> The only thing worth remembering about the past is the cheapest day in it.
    cheapest = prices[0]
    best = 0
    for i in range(1, len(prices)):
        price = prices[i]
        if price < cheapest:
            #> A new low. Every future sale would rather have bought here.
            cheapest = price
        elif price - cheapest > best:
            #> Selling today beats every trade we'd found before.
            best = price - cheapest
    return best


APPROACHES = [
    {
        "id": "brute-force",
        "label": "Every pair of days",
        "fn": brute_force,
        "complexity": {"time": "O(n²)", "space": "O(1)"},
        "viz": {"prices": "array", "buy": "pointer:prices", "sell": "pointer:prices"},
    },
    {
        "id": "one-pass",
        "label": "One pass",
        "fn": one_pass,
        "complexity": {"time": "O(n)", "space": "O(1)"},
        "viz": {"prices": "array", "i": "pointer:prices"},
    },
]
