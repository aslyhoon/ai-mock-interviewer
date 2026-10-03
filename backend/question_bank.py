"""Curated question bank so the app works fully offline (no Gemini key needed).

Structure:
- HR_QUESTIONS: list of plain interview questions
- DSA_BANK: topic -> difficulty -> list of dicts with
    {title, prompt, starter_code, tests: [{input, output}]}
  Starter code + tests are in Python; the code runner supports other
  languages but tests are executed against whatever the user submits.
- CS_QUESTIONS: list of {category, question} across OS / DBMS / CN
"""

import random

HR_QUESTIONS = [
    "Tell me about yourself.",
    "Why do you want this internship?",
    "What is your biggest strength, and give an example of it in action.",
    "Describe a challenging bug or problem you faced and how you solved it.",
    "Where do you see yourself in two years?",
    "Tell me about a project you are most proud of. What was your role?",
    "How do you handle disagreements when working in a team?",
    "Describe a time you had to learn a new technology quickly.",
    "What would you do if you were stuck on a problem for two days?",
    "Why should we hire you over other candidates?",
]

# DSA bank: topic -> difficulty -> questions.
# Each question has Python starter code and stdin/stdout test cases.
DSA_BANK = {
    "arrays": {
        "easy": [
            {
                "title": "Two Sum",
                "prompt": (
                    "Given an array of integers nums and an integer target, return the "
                    "indices of the two numbers that add up to target. Assume exactly one "
                    "solution exists.\n\nInput format: first line n, second line n integers, "
                    "third line target.\nOutput: the two indices separated by a space."
                ),
                "starter_code": "def two_sum(nums, target):\n    # your code here\n    pass\n\nn = int(input())\nnums = list(map(int, input().split()))\ntarget = int(input())\nprint(*two_sum(nums, target))",
                "tests": [
                    {"input": "4\n2 7 11 15\n9\n", "output": "0 1"},
                    {"input": "3\n3 2 4\n6\n", "output": "1 2"},
                    {"input": "2\n3 3\n6\n", "output": "0 1"},
                ],
            },
            {
                "title": "Maximum Subarray Sum",
                "prompt": (
                    "Given an integer array, find the contiguous subarray with the largest "
                    "sum and return that sum (Kadane's algorithm).\n\nInput: first line n, "
                    "second line n integers.\nOutput: the maximum subarray sum."
                ),
                "starter_code": "def max_subarray(nums):\n    # your code here\n    pass\n\nn = int(input())\nnums = list(map(int, input().split()))\nprint(max_subarray(nums))",
                "tests": [
                    {"input": "9\n-2 1 -3 4 -1 2 1 -5 4\n", "output": "6"},
                    {"input": "1\n5\n", "output": "5"},
                    {"input": "3\n-1 -2 -3\n", "output": "-1"},
                ],
            },
        ],
        "medium": [
            {
                "title": "Product of Array Except Self",
                "prompt": (
                    "Given an integer array nums, return an array answer such that answer[i] "
                    "is the product of all elements except nums[i]. Solve in O(n) time "
                    "WITHOUT using division.\n\nInput: first line n, second line n integers.\n"
                    "Output: the answer array on one line."
                ),
                "starter_code": "def product_except_self(nums):\n    # your code here (no division!)\n    pass\n\nn = int(input())\nnums = list(map(int, input().split()))\nprint(*product_except_self(nums))",
                "tests": [
                    {"input": "4\n1 2 3 4\n", "output": "24 12 8 6"},
                    {"input": "5\n-1 1 0 -3 3\n", "output": "0 0 9 0 0"},
                ],
            },
            {
                "title": "Merge Intervals",
                "prompt": (
                    "Given a list of intervals [start, end], merge all overlapping intervals "
                    "and return the merged list.\n\nInput: first line n, then n lines each with "
                    "start end.\nOutput: each merged interval on its own line."
                ),
                "starter_code": "def merge(intervals):\n    # your code here\n    pass\n\nn = int(input())\nintervals = [list(map(int, input().split())) for _ in range(n)]\nfor s, e in merge(intervals):\n    print(s, e)",
                "tests": [
                    {"input": "4\n1 3\n2 6\n8 10\n15 18\n", "output": "1 6\n8 10\n15 18"},
                    {"input": "2\n1 4\n4 5\n", "output": "1 5"},
                ],
            },
        ],
        "hard": [
            {
                "title": "Trapping Rain Water",
                "prompt": (
                    "Given n non-negative integers representing an elevation map, compute "
                    "how much water it can trap after raining.\n\nInput: first line n, second "
                    "line n integers.\nOutput: trapped water units."
                ),
                "starter_code": "def trap(height):\n    # your code here\n    pass\n\nn = int(input())\nheight = list(map(int, input().split()))\nprint(trap(height))",
                "tests": [
                    {"input": "12\n0 1 0 2 1 0 1 3 2 1 2 1\n", "output": "6"},
                    {"input": "6\n4 2 0 3 2 5\n", "output": "9"},
                ],
            },
        ],
    },
    "strings": {
        "easy": [
            {
                "title": "Valid Anagram",
                "prompt": (
                    "Given two strings s and t, return True if t is an anagram of s, else False.\n\n"
                    "Input: two lines, s then t.\nOutput: True or False."
                ),
                "starter_code": "def is_anagram(s, t):\n    # your code here\n    pass\n\ns = input().strip()\nt = input().strip()\nprint(is_anagram(s, t))",
                "tests": [
                    {"input": "anagram\nnagaram\n", "output": "True"},
                    {"input": "rat\ncar\n", "output": "False"},
                ],
            },
        ],
        "medium": [
            {
                "title": "Longest Substring Without Repeating Characters",
                "prompt": (
                    "Given a string s, find the length of the longest substring without "
                    "repeating characters. Aim for O(n).\n\nInput: one line string.\nOutput: the length."
                ),
                "starter_code": "def length_of_longest(s):\n    # your code here\n    pass\n\nprint(length_of_longest(input().strip()))",
                "tests": [
                    {"input": "abcabcbb\n", "output": "3"},
                    {"input": "bbbbb\n", "output": "1"},
                    {"input": "pwwkew\n", "output": "3"},
                ],
            },
        ],
        "hard": [
            {
                "title": "Minimum Window Substring",
                "prompt": (
                    "Given strings s and t, return the minimum window substring of s that "
                    "contains every character of t (including duplicates). Return empty "
                    "string if none exists.\n\nInput: two lines, s then t.\nOutput: the window or empty line."
                ),
                "starter_code": "def min_window(s, t):\n    # your code here\n    pass\n\ns = input().strip()\nt = input().strip()\nprint(min_window(s, t))",
                "tests": [
                    {"input": "ADOBECODEBANC\nABC\n", "output": "BANC"},
                    {"input": "a\naa\n", "output": ""},
                ],
            },
        ],
    },
    "linkedlist": {
        "easy": [
            {
                "title": "Reverse a Linked List (array form)",
                "prompt": (
                    "Reverse the order of the given sequence.\n\nInput: first line n, second "
                    "line n integers.\nOutput: reversed sequence on one line."
                ),
                "starter_code": "n = int(input())\nvals = list(map(int, input().split()))\n# reverse vals\nprint(*reversed(vals))",
                "tests": [
                    {"input": "5\n1 2 3 4 5\n", "output": "5 4 3 2 1"},
                    {"input": "1\n7\n", "output": "7"},
                ],
            },
        ],
        "medium": [
            {
                "title": "Detect Cycle Start (Floyd)",
                "prompt": (
                    "You are given the values visited by a fast/slow pointer walk as a sequence "
                    "of node ids ending when a node repeats. Print the id of the first repeated "
                    "node (the cycle start).\n\nInput: one line of space-separated ids.\nOutput: the first repeated id."
                ),
                "starter_code": "ids = list(map(int, input().split()))\nseen = set()\nfor x in ids:\n    if x in seen:\n        print(x)\n        break\n    seen.add(x)",
                "tests": [
                    {"input": "1 2 3 4 2\n", "output": "2"},
                    {"input": "5 5\n", "output": "5"},
                ],
            },
        ],
        "hard": [
            {
                "title": "Merge K Sorted Lists (k-way)",
                "prompt": (
                    "Merge k sorted sequences into one sorted sequence.\n\nInput: first line k, "
                    "then k lines each: length m followed by m sorted integers.\nOutput: merged sorted sequence."
                ),
                "starter_code": "import heapq\nk = int(input())\nseqs = []\nfor _ in range(k):\n    parts = list(map(int, input().split()))\n    seqs.append(parts[1:])\nmerged = sorted(x for s in seqs for x in s)\nprint(*merged)",
                "tests": [
                    {"input": "3\n3 1 4 5\n3 1 3 4\n2 2 6\n", "output": "1 1 2 3 4 4 5 6"},
                ],
            },
        ],
    },
    "trees": {
        "easy": [
            {
                "title": "Maximum Depth (level-order array)",
                "prompt": (
                    "A binary tree is given as a level-order array with -1 for null nodes. "
                    "Compute its maximum depth.\n\nInput: one line of space-separated integers (-1 = null).\n"
                    "Output: the max depth."
                ),
                "starter_code": "arr = list(map(int, input().split()))\n# compute depth of level-order tree; -1 = null\ndef depth(i):\n    if i >= len(arr) or arr[i] == -1:\n        return 0\n    return 1 + max(depth(2*i+1), depth(2*i+2))\nprint(depth(0))",
                "tests": [
                    {"input": "3 9 20 -1 -1 15 7\n", "output": "3"},
                    {"input": "1 -1 2\n", "output": "2"},
                ],
            },
        ],
        "medium": [
            {
                "title": "Validate BST (inorder array)",
                "prompt": (
                    "You are given the inorder traversal of a binary tree. Print True if it "
                    "could be a valid BST (strictly increasing), else False.\n\nInput: one line "
                    "of space-separated integers.\nOutput: True or False."
                ),
                "starter_code": "arr = list(map(int, input().split()))\nprint(arr == sorted(set(arr)) and len(arr) == len(set(arr)))",
                "tests": [
                    {"input": "1 2 3 4 5\n", "output": "True"},
                    {"input": "1 3 2 5\n", "output": "False"},
                ],
            },
        ],
        "hard": [
            {
                "title": "Lowest Common Ancestor (parent pointers)",
                "prompt": (
                    "Nodes are given with parent pointers: first line n (nodes 1..n) and root r. "
                    "Next n lines: node parent (0 = none). Last line: two nodes a b. "
                    "Print their lowest common ancestor.\n\nOutput: the LCA node id."
                ),
                "starter_code": "n_r = list(map(int, input().split())); n, r = n_r[0], n_r[1]\nparent = {}\nfor _ in range(n):\n    node, p = map(int, input().split()); parent[node] = p\na, b = map(int, input().split())\nanc = set()\nwhile a:\n    anc.add(a); a = parent[a]\nwhile b not in anc:\n    b = parent[b]\nprint(b)",
                "tests": [
                    {"input": "7 1\n1 0\n2 1\n3 1\n4 2\n5 2\n6 3\n7 3\n4 5\n", "output": "2"},
                    {"input": "7 1\n1 0\n2 1\n3 1\n4 2\n5 2\n6 3\n7 3\n4 6\n", "output": "1"},
                ],
            },
        ],
    },
    "dp": {
        "easy": [
            {
                "title": "Climbing Stairs",
                "prompt": (
                    "You are climbing a staircase of n steps; each time you can climb 1 or 2 "
                    "steps. In how many distinct ways can you reach the top?\n\nInput: n.\nOutput: ways."
                ),
                "starter_code": "n = int(input())\na, b = 1, 1\nfor _ in range(n):\n    a, b = b, a + b\nprint(a)",
                "tests": [
                    {"input": "2\n", "output": "2"},
                    {"input": "5\n", "output": "8"},
                ],
            },
        ],
        "medium": [
            {
                "title": "Coin Change (min coins)",
                "prompt": (
                    "Given coin denominations and an amount, return the fewest coins needed "
                    "to make that amount, or -1 if impossible.\n\nInput: first line m (coins count), "
                    "second line m denominations, third line amount.\nOutput: min coins or -1."
                ),
                "starter_code": "m = int(input())\ncoins = list(map(int, input().split()))\namount = int(input())\nINF = float('inf')\ndp = [0] + [INF]*amount\nfor x in range(1, amount+1):\n    dp[x] = min((dp[x-c]+1 for c in coins if c <= x), default=INF)\nprint(dp[amount] if dp[amount] != INF else -1)",
                "tests": [
                    {"input": "3\n1 2 5\n11\n", "output": "3"},
                    {"input": "1\n2\n3\n", "output": "-1"},
                ],
            },
        ],
        "hard": [
            {
                "title": "Edit Distance",
                "prompt": (
                    "Given two strings, compute the minimum number of operations (insert, delete, "
                    "replace) to convert one into the other.\n\nInput: two lines.\nOutput: the edit distance."
                ),
                "starter_code": "a = input().strip()\nb = input().strip()\nm, n = len(a), len(b)\ndp = list(range(n+1))\nfor i in range(1, m+1):\n    ndp = [i] + [0]*n\n    for j in range(1, n+1):\n        ndp[j] = min(dp[j]+1, ndp[j-1]+1, dp[j-1] + (a[i-1] != b[j-1]))\n    dp = ndp\nprint(dp[n])",
                "tests": [
                    {"input": "horse\nros\n", "output": "3"},
                    {"input": "intention\nexecution\n", "output": "5"},
                ],
            },
        ],
    },
}

CS_QUESTIONS = [
    {"category": "os", "question": "What is the difference between a process and a thread?"},
    {"category": "os", "question": "Explain deadlock. What are the four Coffman conditions, and how would you prevent it?"},
    {"category": "os", "question": "What is virtual memory and how does paging work?"},
    {"category": "os", "question": "Compare mutex vs semaphore with a real-world example."},
    {"category": "dbms", "question": "Explain ACID properties with an example of a bank transfer."},
    {"category": "dbms", "question": "What is normalization? Explain 1NF, 2NF and 3NF."},
    {"category": "dbms", "question": "Difference between SQL and NoSQL — when would you pick each?"},
    {"category": "dbms", "question": "What is an index in a database and how does it speed up queries?"},
    {"category": "cn", "question": "Explain the TCP 3-way handshake. Why three steps and not two?"},
    {"category": "cn", "question": "Difference between TCP and UDP — give use cases for each."},
    {"category": "cn", "question": "What happens when you type a URL and press enter? Walk me through it."},
    {"category": "cn", "question": "What is DNS and how does resolution work?"},
]

DSA_TOPICS = list(DSA_BANK.keys())


def get_dsa_question(topic: str, difficulty: str, exclude_titles: set | None = None):
    """Pick a random DSA question, avoiding ones already asked this session."""
    pool = DSA_BANK.get(topic, {}).get(difficulty, [])
    if exclude_titles:
        pool = [q for q in pool if q["title"] not in exclude_titles]
    if not pool:  # fall back to any question in the topic
        pool = [q for qs in DSA_BANK.get(topic, {}).values() for q in qs
                if not exclude_titles or q["title"] not in exclude_titles]
    return random.choice(pool) if pool else None


def sanity_check() -> list[str]:
    """Returns a list of problems (empty list = bank is healthy)."""
    problems = []
    for topic, diffs in DSA_BANK.items():
        for diff, qs in diffs.items():
            if not qs:
                problems.append(f"empty: {topic}/{diff}")
            for q in qs:
                for key in ("title", "prompt", "starter_code", "tests"):
                    if not q.get(key):
                        problems.append(f"missing {key}: {topic}/{diff}/{q.get('title')}")
                if not q.get("tests"):
                    problems.append(f"no tests: {topic}/{diff}/{q.get('title')}")
    if not HR_QUESTIONS:
        problems.append("HR_QUESTIONS empty")
    if not CS_QUESTIONS:
        problems.append("CS_QUESTIONS empty")
    return problems
