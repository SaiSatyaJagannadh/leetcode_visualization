META = {
    "slug": "hand-of-straights",
    "title": "Hand of Straights",
    "pattern": "Greedy",
    "difficulty": "Medium",
    "leetcode": 846,
    "prompt": "Decide whether a hand of cards can be split entirely into groups of a given size, each group being consecutive numbers.",
    "examples": [
        {"input": "hand = [1,2,3,6,2,3,4,7,8], groupSize = 3", "output": "true"},
        {"input": "hand = [1,2,3,4,5], groupSize = 4", "output": "false"},
    ],
    "constraints": ["1 <= len(hand) <= 10^4"],
}

VARIANTS = [
    {"id": "typical", "label": "Splits cleanly", "input": {"hand": [1, 2, 3, 6, 2, 3, 4, 7, 8], "size": 3}},
    {"id": "edge", "label": "Wrong total", "input": {"hand": [1, 2, 3, 4, 5], "size": 4}},
    {"id": "worst-case", "label": "Gap breaks it", "input": {"hand": [1, 2, 4, 5], "size": 2}},
]


def smallest_first(hand, size):
    if len(hand) % size != 0:
        #> Not divisible, so no arrangement can possibly work.
        return False
    counts = {}
    for c in hand:
        counts[c] = counts.get(c, 0) + 1
    for card in sorted(counts):
        need = counts.get(card, 0)
        if need <= 0:
            continue
        #> The smallest remaining card has no smaller partner, so it *must* start
        #> a group. That forces the whole group, leaving no choice to regret.
        for step in range(size):
            have = counts.get(card + step, 0)
            if have < need:
                #> Not enough of a required consecutive card.
                return False
            counts[card + step] = have - need
    return True


def peel_groups(hand, size):
    #> No counting map: sort the cards and physically remove each group. Slower,
    #> but it makes the forced choice obvious — the first card left is always
    #> the start of the next group, because nothing smaller survives to precede it.
    if len(hand) % size != 0:
        return False
    rest = sorted(hand)
    while rest:
        start = rest[0]
        for step in range(size):
            want = start + step
            if want not in rest:
                #> A required consecutive card is missing, so no arrangement works.
                return False
            #> Remove one copy, not all of them — duplicates belong to other groups.
            rest.remove(want)
    return True


APPROACHES = [
    {"id": "peel", "label": "Sort and remove each group", "fn": peel_groups,
     "complexity": {"time": "O(n\u00b2)", "space": "O(n)"},
     "viz": {"hand": "array", "rest": "array"}},
    {"id": "smallest-first", "label": "The smallest card forces its group", "fn": smallest_first,
     "complexity": {"time": "O(n log n)", "space": "O(n)"},
     "viz": {"hand": "array", "counts": "map"}},
]
