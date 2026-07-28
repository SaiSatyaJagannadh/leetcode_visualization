"""The problem set and its pattern grouping — the roadmap the site is built around.

Facts only: slug, title, LeetCode number, difficulty, pattern. Problem statements
and examples are written from scratch in each solution.py, never copied.

Order matters: patterns are listed in learning order, and problems within a
pattern go easiest first, so the landing page reads as a route through the set.
"""

PATTERNS = [
    "Arrays & Hashing",
    "Two Pointers",
    "Sliding Window",
    "Stack",
    "Binary Search",
    "Linked List",
    "Trees",
    "Tries",
    "Heap / Priority Queue",
    "Backtracking",
    "Graphs",
    "Advanced Graphs",
    "1-D Dynamic Programming",
    "2-D Dynamic Programming",
    "Greedy",
    "Intervals",
    "Math & Geometry",
    "Bit Manipulation",
]

# (leetcode number, title, difficulty)
SEED = {
    "Arrays & Hashing": [
        (217, "Contains Duplicate", "Easy"),
        (242, "Valid Anagram", "Easy"),
        (1, "Two Sum", "Easy"),
        (49, "Group Anagrams", "Medium"),
        (347, "Top K Frequent Elements", "Medium"),
        (271, "Encode and Decode Strings", "Medium"),
        (238, "Product of Array Except Self", "Medium"),
        (36, "Valid Sudoku", "Medium"),
        (128, "Longest Consecutive Sequence", "Medium"),
    ],
    "Two Pointers": [
        (125, "Valid Palindrome", "Easy"),
        (167, "Two Sum II", "Medium"),
        (15, "3Sum", "Medium"),
        (11, "Container With Most Water", "Medium"),
        (42, "Trapping Rain Water", "Hard"),
    ],
    "Sliding Window": [
        (121, "Best Time to Buy and Sell Stock", "Easy"),
        (3, "Longest Substring Without Repeating Characters", "Medium"),
        (424, "Longest Repeating Character Replacement", "Medium"),
        (567, "Permutation in String", "Medium"),
        (76, "Minimum Window Substring", "Hard"),
        (239, "Sliding Window Maximum", "Hard"),
    ],
    "Stack": [
        (20, "Valid Parentheses", "Easy"),
        (155, "Min Stack", "Medium"),
        (150, "Evaluate Reverse Polish Notation", "Medium"),
        (22, "Generate Parentheses", "Medium"),
        (739, "Daily Temperatures", "Medium"),
        (853, "Car Fleet", "Medium"),
        (84, "Largest Rectangle in Histogram", "Hard"),
    ],
    "Binary Search": [
        (704, "Binary Search", "Easy"),
        (74, "Search a 2D Matrix", "Medium"),
        (875, "Koko Eating Bananas", "Medium"),
        (153, "Find Minimum in Rotated Sorted Array", "Medium"),
        (33, "Search in Rotated Sorted Array", "Medium"),
        (981, "Time Based Key-Value Store", "Medium"),
        (4, "Median of Two Sorted Arrays", "Hard"),
    ],
    "Linked List": [
        (206, "Reverse Linked List", "Easy"),
        (21, "Merge Two Sorted Lists", "Easy"),
        (143, "Reorder List", "Medium"),
        (19, "Remove Nth Node From End of List", "Medium"),
        (138, "Copy List With Random Pointer", "Medium"),
        (2, "Add Two Numbers", "Medium"),
        (141, "Linked List Cycle", "Easy"),
        (287, "Find the Duplicate Number", "Medium"),
        (146, "LRU Cache", "Medium"),
        (23, "Merge K Sorted Lists", "Hard"),
        (25, "Reverse Nodes in K-Group", "Hard"),
    ],
    "Trees": [
        (226, "Invert Binary Tree", "Easy"),
        (104, "Maximum Depth of Binary Tree", "Easy"),
        (543, "Diameter of Binary Tree", "Easy"),
        (110, "Balanced Binary Tree", "Easy"),
        (100, "Same Tree", "Easy"),
        (572, "Subtree of Another Tree", "Easy"),
        (235, "Lowest Common Ancestor of a BST", "Medium"),
        (102, "Binary Tree Level Order Traversal", "Medium"),
        (199, "Binary Tree Right Side View", "Medium"),
        (1448, "Count Good Nodes in Binary Tree", "Medium"),
        (98, "Validate Binary Search Tree", "Medium"),
        (230, "Kth Smallest Element in a BST", "Medium"),
        (105, "Construct Binary Tree From Preorder and Inorder", "Medium"),
        (124, "Binary Tree Maximum Path Sum", "Hard"),
        (297, "Serialize and Deserialize Binary Tree", "Hard"),
    ],
    "Tries": [
        (208, "Implement Trie", "Medium"),
        (211, "Design Add and Search Words", "Medium"),
        (212, "Word Search II", "Hard"),
    ],
    "Heap / Priority Queue": [
        (703, "Kth Largest Element in a Stream", "Easy"),
        (1046, "Last Stone Weight", "Easy"),
        (973, "K Closest Points to Origin", "Medium"),
        (215, "Kth Largest Element in an Array", "Medium"),
        (621, "Task Scheduler", "Medium"),
        (355, "Design Twitter", "Medium"),
        (295, "Find Median From Data Stream", "Hard"),
    ],
    "Backtracking": [
        (78, "Subsets", "Medium"),
        (39, "Combination Sum", "Medium"),
        (46, "Permutations", "Medium"),
        (90, "Subsets II", "Medium"),
        (40, "Combination Sum II", "Medium"),
        (79, "Word Search", "Medium"),
        (131, "Palindrome Partitioning", "Medium"),
        (17, "Letter Combinations of a Phone Number", "Medium"),
        (51, "N-Queens", "Hard"),
    ],
    "Graphs": [
        (200, "Number of Islands", "Medium"),
        (133, "Clone Graph", "Medium"),
        (695, "Max Area of Island", "Medium"),
        (417, "Pacific Atlantic Water Flow", "Medium"),
        (130, "Surrounded Regions", "Medium"),
        (994, "Rotting Oranges", "Medium"),
        (286, "Walls and Gates", "Medium"),
        (207, "Course Schedule", "Medium"),
        (210, "Course Schedule II", "Medium"),
        (684, "Redundant Connection", "Medium"),
        (323, "Number of Connected Components", "Medium"),
        (261, "Graph Valid Tree", "Medium"),
        (127, "Word Ladder", "Hard"),
    ],
    "Advanced Graphs": [
        (332, "Reconstruct Itinerary", "Hard"),
        (1584, "Min Cost to Connect All Points", "Medium"),
        (743, "Network Delay Time", "Medium"),
        (778, "Swim in Rising Water", "Hard"),
        (269, "Alien Dictionary", "Hard"),
        (787, "Cheapest Flights Within K Stops", "Medium"),
    ],
    "1-D Dynamic Programming": [
        (70, "Climbing Stairs", "Easy"),
        (746, "Min Cost Climbing Stairs", "Easy"),
        (198, "House Robber", "Medium"),
        (213, "House Robber II", "Medium"),
        (5, "Longest Palindromic Substring", "Medium"),
        (647, "Palindromic Substrings", "Medium"),
        (91, "Decode Ways", "Medium"),
        (322, "Coin Change", "Medium"),
        (152, "Maximum Product Subarray", "Medium"),
        (139, "Word Break", "Medium"),
        (300, "Longest Increasing Subsequence", "Medium"),
        (416, "Partition Equal Subset Sum", "Medium"),
    ],
    "2-D Dynamic Programming": [
        (62, "Unique Paths", "Medium"),
        (1143, "Longest Common Subsequence", "Medium"),
        (309, "Buy and Sell Stock With Cooldown", "Medium"),
        (518, "Coin Change II", "Medium"),
        (494, "Target Sum", "Medium"),
        (97, "Interleaving String", "Medium"),
        (329, "Longest Increasing Path in a Matrix", "Hard"),
        (115, "Distinct Subsequences", "Hard"),
        (72, "Edit Distance", "Medium"),
        (312, "Burst Balloons", "Hard"),
        (10, "Regular Expression Matching", "Hard"),
    ],
    "Greedy": [
        (53, "Maximum Subarray", "Medium"),
        (55, "Jump Game", "Medium"),
        (45, "Jump Game II", "Medium"),
        (134, "Gas Station", "Medium"),
        (846, "Hand of Straights", "Medium"),
        (1899, "Merge Triplets to Form Target", "Medium"),
        (763, "Partition Labels", "Medium"),
        (678, "Valid Parenthesis String", "Medium"),
    ],
    "Intervals": [
        (57, "Insert Interval", "Medium"),
        (56, "Merge Intervals", "Medium"),
        (435, "Non-Overlapping Intervals", "Medium"),
        (252, "Meeting Rooms", "Easy"),
        (253, "Meeting Rooms II", "Medium"),
        (1851, "Minimum Interval to Include Each Query", "Hard"),
    ],
    "Math & Geometry": [
        (48, "Rotate Image", "Medium"),
        (54, "Spiral Matrix", "Medium"),
        (73, "Set Matrix Zeroes", "Medium"),
        (202, "Happy Number", "Easy"),
        (66, "Plus One", "Easy"),
        (50, "Pow(x, n)", "Medium"),
        (43, "Multiply Strings", "Medium"),
        (2013, "Detect Squares", "Medium"),
    ],
    "Bit Manipulation": [
        (136, "Single Number", "Easy"),
        (191, "Number of 1 Bits", "Easy"),
        (338, "Counting Bits", "Easy"),
        (190, "Reverse Bits", "Easy"),
        (268, "Missing Number", "Easy"),
        (371, "Sum of Two Integers", "Medium"),
        (7, "Reverse Integer", "Medium"),
    ],
}


# Where our slug differs from LeetCode's, so the outbound links don't 404.
LC_SLUG = {
    "two-sum-ii": "two-sum-ii-input-array-is-sorted",
    "construct-binary-tree-from-preorder-and-inorder":
        "construct-binary-tree-from-preorder-and-inorder-traversal",
    "buy-and-sell-stock-with-cooldown": "best-time-to-buy-and-sell-stock-with-cooldown",
    "design-add-and-search-words": "design-add-and-search-words-data-structure",
    "implement-trie": "implement-trie-prefix-tree",
    "lowest-common-ancestor-of-a-bst": "lowest-common-ancestor-of-a-binary-search-tree",
    "number-of-connected-components": "number-of-connected-components-in-an-undirected-graph",
}


def slugify(title):
    keep = "".join(c if c.isalnum() or c in " -" else "" for c in title.lower())
    return "-".join(keep.split())


def rows():
    """(slug, title, pattern, difficulty, leetcode, pattern_order, order)."""
    for pi, pattern in enumerate(PATTERNS):
        for i, (num, title, diff) in enumerate(SEED[pattern]):
            slug = slugify(title)
            yield slug, title, pattern, diff, num, LC_SLUG.get(slug, slug), pi, i


if __name__ == "__main__":
    all_rows = list(rows())
    print(f"{len(all_rows)} problems across {len(PATTERNS)} patterns")
    for p in PATTERNS:
        print(f"  {len(SEED[p]):3}  {p}")
