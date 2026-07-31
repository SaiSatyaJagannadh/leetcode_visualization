META = {
    "slug": "encode-and-decode-strings",
    "title": "Encode and Decode Strings",
    "pattern": "Arrays & Hashing",
    "difficulty": "Medium",
    "leetcode": 271,
    "prompt": "Join a list of strings into one string, and split it back into the original list. The strings may contain any characters, including whatever separator you pick.",
    "examples": [
        {"input": 'strs = ["neet","code"]', "output": '"4#neet4#code" then back to ["neet","code"]'},
        {"input": 'strs = ["","a"]', "output": "empty strings survive the round trip"},
    ],
    "constraints": ["0 <= len(strs) <= 200", "Any characters are possible"],
}

VARIANTS = [
    {"id": "typical", "label": "Typical", "input": {"strs": ["neet", "code", "love"]}},
    {"id": "edge", "label": "Empty string", "input": {"strs": ["", "a"]}},
    {"id": "worst-case", "label": "Contains the separator", "input": {"strs": ["a#b", "2#c"]}},
]


def length_prefix(strs):
    #> Any separator character could appear inside a string, so no separator alone
    #> is safe. Writing the length first means the decoder never has to guess:
    #> it reads exactly that many characters, whatever they contain.
    parts = []
    for s in strs:
        parts.append(str(len(s)) + "#" + s)
    encoded = "".join(parts)

    out = []
    i = 0
    while i < len(encoded):
        #> Read digits up to the marker; that number is the payload length.
        j = i
        while encoded[j] != "#":
            j += 1
        size = int(encoded[i:j])
        #> Then take exactly `size` characters, no interpretation needed.
        out.append(encoded[j + 1:j + 1 + size])
        i = j + 1 + size
    return out


def escaped_separator(strs):
    #> The other way round: keep a separator, but make it impossible for a
    #> payload to contain one. Every literal # becomes ##, so a single # can
    #> only ever mean "boundary".
    parts = []
    for s in strs:
        parts.append(s.replace("#", "##"))
    encoded = "#;".join(parts)

    out = []
    cur = ""
    i = 0
    while i < len(encoded):
        if encoded[i] == "#" and i + 1 < len(encoded) and encoded[i + 1] == "#":
            #> A doubled # is one real # of payload.
            cur += "#"
            i += 2
        elif encoded[i] == "#" and i + 1 < len(encoded) and encoded[i + 1] == ";":
            #> A lone # followed by ; is the boundary we reserved.
            out.append(cur)
            cur = ""
            i += 2
        else:
            cur += encoded[i]
            i += 1
    #> The final chunk has no trailing separator, so it is flushed here.
    out.append(cur)
    return out


APPROACHES = [
    {"id": "escaped", "label": "Escaped separator", "fn": escaped_separator,
     "complexity": {"time": "O(total chars)", "space": "O(total chars)"},
     "viz": {"strs": "array", "parts": "queue", "out": "queue"}},
    {"id": "length-prefix", "label": "Length-prefixed chunks", "fn": length_prefix,
     "complexity": {"time": "O(total chars)", "space": "O(total chars)"},
     "viz": {"strs": "array", "parts": "queue", "out": "queue"}},
]
