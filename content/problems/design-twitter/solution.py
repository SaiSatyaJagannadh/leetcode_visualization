META = {
    "slug": "design-twitter",
    "title": "Design Twitter",
    "pattern": "Heap / Priority Queue",
    "difficulty": "Medium",
    "leetcode": 355,
    "prompt": "Support posting, following, and reading a feed of the ten most recent posts from yourself and everyone you follow, newest first.",
    "examples": [
        {"input": "user 1 posts 5, getNewsFeed(1)", "output": "[5]"},
        {"input": "1 follows 2, 2 posts 6, getNewsFeed(1)", "output": "[6,5]"},
        {"input": "1 unfollows 2, getNewsFeed(1)", "output": "[5]"},
    ],
    "constraints": ["At most 3 * 10^4 calls", "Feed holds at most 10 posts"],
}

VARIANTS = [
    {"id": "typical", "label": "Follow and read",
     "input": {"ops": [["post", 1, 5], ["follow", 1, 2], ["post", 2, 6], ["feed", 1, 0]]}},
    {"id": "edge", "label": "No follows",
     "input": {"ops": [["post", 1, 5], ["feed", 1, 0]]}},
    {"id": "worst-case", "label": "Unfollow again",
     "input": {"ops": [["post", 1, 5], ["follow", 1, 2], ["post", 2, 6], ["unfollow", 1, 2], ["feed", 1, 0]]}},
]

FEED_SIZE = 10


def timeline(ops):
    #> A global clock is what makes posts from different users comparable.
    clock = [0]
    posts = {}
    follows = {}
    out = []
    for op in ops:
        kind, user, arg = op[0], op[1], op[2]
        if kind == "post":
            clock[0] += 1
            #> Store newest-first so a feed read never has to sort a user's own posts.
            posts.setdefault(user, []).insert(0, [clock[0], arg])
        elif kind == "follow":
            follows.setdefault(user, {})[arg] = True
        elif kind == "unfollow":
            if user in follows and arg in follows[user]:
                del follows[user][arg]
        else:
            #> Merge the heads of each followed timeline, newest first. Only ten
            #> are wanted, so we never merge more than ten deep.
            sources = [user]
            for other in follows.get(user, {}):
                sources.append(other)
            merged = []
            for s in sources:
                for entry in posts.get(s, []):
                    merged.append(entry)
            merged.sort(key=lambda e: -e[0])
            feed = []
            for entry in merged[:FEED_SIZE]:
                feed.append(entry[1])
            out.append(feed)
    return out


def merge_heads(ops):
    #> Never build the full list. Keep a cursor into each followed timeline and
    #> repeatedly take whichever head is newest — ten times, then stop. Sorting
    #> every post to keep ten of them is the work this avoids.
    clock = [0]
    posts = {}
    follows = {}
    out = []
    for op in ops:
        kind, user, arg = op[0], op[1], op[2]
        if kind == "post":
            clock[0] += 1
            posts.setdefault(user, []).insert(0, [clock[0], arg])
        elif kind == "follow":
            follows.setdefault(user, {})[arg] = True
        elif kind == "unfollow":
            if user in follows and arg in follows[user]:
                del follows[user][arg]
        else:
            sources = [user]
            for other in follows.get(user, {}):
                sources.append(other)
            #> One cursor per source, all starting at that source's newest post.
            at = {}
            for s in sources:
                at[s] = 0
            feed = []
            while len(feed) < FEED_SIZE:
                #> Pick the newest head across every cursor.
                pick = None
                for s in sources:
                    row = posts.get(s, [])
                    if at[s] < len(row):
                        if pick is None or row[at[s]][0] > posts[pick][at[pick]][0]:
                            pick = s
                if pick is None:
                    #> Every timeline is exhausted, so the feed is short.
                    break
                feed.append(posts[pick][at[pick]][1])
                at[pick] += 1
            out.append(feed)
    return out


APPROACHES = [
    {"id": "merge-heads", "label": "Merge the timeline heads", "fn": merge_heads,
     "complexity": {"time": "O(feed \u00b7 sources)", "space": "O(sources)"},
     "viz": {"posts": "map", "follows": "map", "at": "map", "feed": "queue"}},
    {"id": "merge", "label": "Merge timelines by timestamp", "fn": timeline,
     "complexity": {"time": "O(f log f) per feed", "space": "O(posts)"},
     "viz": {"posts": "map", "follows": "map", "out": "queue", "merged": "array"}},
]
