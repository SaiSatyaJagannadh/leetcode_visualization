"""Replay every committed trace through the Streamlit reader.

`streamlit_app.py` re-implements `lib/fold.ts` in Python. Two readers of the same
artifacts is exactly the kind of thing that drifts silently, so this walks every
step of every variant of every trace: the fold must not dangle a path, the step
line must index into the source, and the renderer must survive every shape the
corpus contains.

    python3 pipeline/check_streamlit.py
"""

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# budget() counts against the same store the API's quota uses, and with no KV
# credentials that store is a file. Point it somewhere disposable before anything
# can import _lib, so a test run cannot spend the developer's real day budget.
os.environ["KV_LOCAL_PATH"] = str(Path(tempfile.mkdtemp()) / "kv.json")

from streamlit_app import (  # noqa: E402
    render_state,
    resolve,
    source_html,
    state_at,
    touched,
)

fails = []
traces = sorted((ROOT / "traces").glob("*.json"))
steps_seen = 0

for path in traces:
    if path.name == "index.json":
        continue
    trace = json.loads(path.read_text())
    for approach in trace["approaches"]:
        source, viz, layout = approach["source"], approach["viz"], approach["layout"]
        for variant in approach["variants"]:
            steps = variant["steps"]
            where = f'{trace["slug"]}/{approach["id"]}/{variant["id"]}'
            for i, step in enumerate(steps):
                if not 0 <= step["line"] < len(source):
                    fails.append(f'{where} step {i}: line {step["line"]} outside source')
                    continue
                try:
                    state = state_at(steps, i)
                    source_html(source, step["line"])
                    render_state(state, viz, layout, touched(step))
                except Exception as e:  # noqa: BLE001 — any crash is the failure
                    fails.append(f"{where} step {i}: {type(e).__name__}: {e}")
                steps_seen += 1

print(f"{len(traces) - 1} traces, {steps_seen} steps replayed")


# The ask box is a lookup over the same index, so it is checkable offline. These
# are the phrasings a reader actually types; each one has been wrong once.
index = json.loads((ROOT / "traces" / "index.json").read_text())
cases = [
    ("leetcode 25", "reverse-nodes-in-k-group"),
    ("25", "reverse-nodes-in-k-group"),
    ("lc 1", "two-sum"),
    ("two sum", "two-sum"),
    ("Reverse Linked List", "reverse-linked-list"),
    ("revrse linked list", "reverse-linked-list"),  # fuzzy, for typos
    ("leetcode 1882", None),  # outside the 150 — say so, do not guess
    ("xyzzy", None),
]
for query, want in cases:
    got, reply = resolve(query, index["problems"])
    if got != want:
        fails.append(f"resolve({query!r}) gave {got!r}, wanted {want!r}")
    if not reply:
        fails.append(f"resolve({query!r}) gave no reply")

# A pattern name lists the pattern rather than landing on the one title that
# happens to contain those words.
got, reply = resolve("sliding window", index["problems"])
if got is not None or "Sliding Window" not in reply:
    fails.append(f"resolve('sliding window') should list the pattern, gave {got!r}")

# Explain grounds the teacher on resolve()'s reply, but only when that reply is a
# fact about the corpus — the gate is "a slug, or a bolded name". A miss must
# therefore bold nothing, or the teacher is handed "No match. Try a LeetCode
# number" as authoritative and explains the search box instead of an algorithm.
for query in ("xyzzy", "", "   "):
    got, reply = resolve(query, index["problems"])
    if got or reply.startswith("**"):
        fails.append(f"resolve({query!r}) reads as a corpus fact: {reply!r}")

print(f"ask box: {len(cases) + 4} queries")


# The 150 are built by tracer/build.py from Python that really ran. The other
# half of the Ask view is a trace a model wrote, which obeys the same schema and
# none of the same habits — and it had never been rendered in a check. This is a
# real generator output kept verbatim, `nums: grid` on a flat list and all.
made = json.loads((ROOT / "fixtures" / "generated.json").read_text())
gen_steps = 0
for approach in made["approaches"]:
    for variant in approach["variants"]:
        steps = variant["steps"]
        for i, step in enumerate(steps):
            try:
                render_state(state_at(steps, i), approach["viz"], approach["layout"], touched(step))
                source_html(approach["source"], step["line"])
            except Exception as e:  # noqa: BLE001
                fails.append(f'generated/{approach["id"]}/{variant["id"]} step {i}: '
                             f"{type(e).__name__}: {e}")
            gen_steps += 1
print(f"generated trace: {gen_steps} steps replayed")


# The 150 are built by tracer/build.py and their viz specs are always honest.
# A generated trace writes its own, and gemini has declared `grid` on a flat
# list — which used to send an int through the row loop and take the whole page
# down. The reader must render something sane for any kind on any value.
for spec, state in (
    ({"nums": "grid"}, {"nums": [1, 2, 3]}),          # rows that are not rows
    ({"s": "grid"}, {"s": ["ab", "cd"]}),             # rows of characters
    ({"n": "node"}, {"n": 5}),                        # a counter labelled a node
    ({"g": "graph"}, {"g": []}),                      # an empty adjacency list
    ({"x": "heap"}, {"x": None}),
):
    try:
        render_state(state, spec, {}, set())
    except Exception as e:  # noqa: BLE001 — any crash is the failure
        fails.append(f"viz {spec} on {state} crashed the reader: {type(e).__name__}: {e}")


# The leetcode-teacher skill ships its patterns as prose, so the mapping from
# our eighteen pattern names to its ten is hand-written and can rot silently:
# rename a heading in the skill and the template just stops appearing.
from streamlit_app import PATTERN_MAP, teacher_sections, teaching  # noqa: E402

sections = teacher_sections()
if not sections:
    fails.append("the leetcode-teacher reference parsed to nothing")
for ours, theirs in PATTERN_MAP.items():
    if theirs not in sections:
        fails.append(f"PATTERN_MAP sends {ours!r} to {theirs!r}, which the skill does not define")
    if not any(p["pattern"] == ours for p in index["problems"]):
        fails.append(f"PATTERN_MAP names {ours!r}, which is not a pattern in the corpus")
mapped = [p for p in index["patterns"] if teaching(p)]
print(f"teacher: {len(sections)} patterns, {len(mapped)}/{len(index['patterns'])} mapped")


# Everything above tests pure functions, which is exactly the class of bug it
# cannot catch: the app has now crashed twice on Streamlit's own rules about
# when session state may be written, and both times the functions were fine and
# the *script* was not. AppTest runs the real script, so a click that raises is
# a failed check rather than a red box on the deployed site.
from streamlit.testing.v1 import AppTest  # noqa: E402

app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=120).run()


def ok(name, cond, detail=""):
    if not cond:
        fails.append(f"{name} {detail}".strip())


ok("the roadmap renders", not app.exception, str(app.exception))
ok("every problem has a row", len(app.button) == len(index["problems"]), str(len(app.button)))

app.button(key="go_two-sum").click().run()
ok("a row click opens that problem", not app.exception and app.session_state.slug == "two-sum")
ok("opening a problem counts it as watched", "two-sum" in app.session_state.seen)
ok("the player renders its transport", any(b.key.startswith("tp_") for b in app.button))

app.button(key="nav_next").click().run()
ok("next walks to the following problem",
   not app.exception and app.session_state.slug != "two-sum")
app.button(key="nav_back").click().run()
ok("back returns to the roadmap", not app.exception and not app.session_state.open)

# Asking for one of the 150 by name must PLAY it, in the Ask view, through the
# same panel the Problems page uses — not answer in prose and point elsewhere.
# The player is what makes this site the thing it is; an Ask view that only
# talks is the bug this asserts against. It also covers the crash that used to
# happen here, when switching pages wrote a widget's key after instantiation.
app.radio[0].set_value("Ask").run()  # positional: the fix is what names this key
ok("the ask view renders", not app.exception, str(app.exception))
app.session_state.askmode = "Trace it"
app.chat_input[0].set_value("leetcode 1").run()
ok("a traced problem asked for by number does not crash", not app.exception, str(app.exception))
ok("...and plays inside the Ask view", app.session_state.shown == "two-sum"
   and app.session_state.view == "Ask",
   f'shown={app.session_state.shown} view={app.session_state.view}')
ok("...through the same player the Problems page uses",
   any(b.key.startswith("tp_") and "ask:two-sum" in b.key for b in app.button),
   str([b.key for b in app.button][:4]))
ok("...with the problem's own title and prompt",
   any("Two Sum" in m.value for m in app.markdown),
   "no title")


# And the same trace through the app. Seeded rather than generated: the render
# path is what is under test, not the model or the network.
app.session_state.shown = None
app.session_state.traced = made
app.run()
ok("a generated trace renders in the Ask view", not app.exception, str(app.exception))
ok("...through the same player as the 150",
   any(b.key.startswith("tp_") and "generated" in b.key for b in app.button))
ok("...and says it is not one of them",
   any("generated, not committed" in m.value for m in app.markdown))

print("app: 14 interactions")


# The app is a public URL holding my API keys, so the caps are the load-bearing
# part. The per-session ones are visible and reset on reload — that is on
# purpose, and it is why they are not what is checked here. This is the one that
# has to survive a reload, because a reload is the whole bypass.
import streamlit_app as sa  # noqa: E402

sa.DAY_CAP["ask"] = 2
ok("the day budget hands out exactly its cap",
   [sa.budget("ask") for _ in range(3)] == [True, True, False])
ok("reloading does not refill it", sa.budget("ask") is False)
ok("each path draws on its own budget", sa.budget("gen") is True)
print("caps: day budget holds")


# Watched progress rides in the URL, so the token is caller-supplied input on one
# side and someone's study record on the other. A wrong tick is worse than a
# missing one, so every failure here has to fail to empty.
from streamlit_app import all_slugs, decode_seen, encode_seen  # noqa: E402

SLUGS = all_slugs()
ok("every problem is in the slug list", len(SLUGS) == len(index["problems"]))

for case in [set(), {"two-sum"}, {SLUGS[0], SLUGS[-1]}, set(SLUGS[::3]), set(SLUGS)]:
    ok(f"a set of {len(case)} round-trips", decode_seen(encode_seen(case, SLUGS), SLUGS) == case)

full = encode_seen(set(SLUGS), SLUGS)
ok("the token stays short enough for a URL", len(full) < 64, f"{len(full)} chars")

# The bitmask is positional, so a token minted against a different corpus would
# tick the wrong rows — confidently, and invisibly. The fingerprint is what makes
# that case detectable rather than plausible.
shifted = ["aardvark-problem"] + SLUGS[:-1]
ok("a token from a different corpus is discarded",
   decode_seen(encode_seen({SLUGS[0]}, SLUGS), shifted) == set())

for junk in ["", "!!!!", "zzzz", "zzzznotbase64!!", SLUGS[0], full[:3]]:
    got = decode_seen(junk, SLUGS)
    ok(f"junk token {junk[:12]!r} decodes to empty", got == set(), str(got)[:60])

# A token clipped by a chat app or an editor keeps its fingerprint, so it is a
# real record with its tail missing rather than junk. Reading the surviving bytes
# loses the later problems and never invents an earlier one — the direction this
# is allowed to be wrong in.
clipped = encode_seen(set(SLUGS), SLUGS)[:12]
ok("a clipped token never reports more than was watched",
   decode_seen(clipped, SLUGS) < set(SLUGS), str(len(decode_seen(clipped, SLUGS))))
ok("a clipped token still recovers what survived",
   decode_seen(clipped, SLUGS) == set(SLUGS[:48]), str(len(decode_seen(clipped, SLUGS))))
# The encode/decode pair being correct says nothing about the app actually
# seeding itself from the URL, which is the half a reader would notice. Boot a
# second app with a token in the query string and check the ticks come back.
carried = encode_seen({"two-sum", SLUGS[-1]}, SLUGS)
app2 = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=120)
app2.query_params["p"] = carried
app2.run()
ok("a fresh load with a token restores the watched set",
   not app2.exception and app2.session_state.seen == {"two-sum", SLUGS[-1]},
   str(getattr(app2, "exception", "")) or str(app2.session_state.seen)[:80])
ok("a restored session is told its progress rides in the link",
   any("Bookmark this page" in c.value for c in app2.caption), "no bookmark hint rendered")

app3 = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=120)
app3.query_params["p"] = "not-a-real-token"
app3.run()
ok("a junk token loads the app rather than breaking it",
   not app3.exception and app3.session_state.seen == set(), str(app3.exception))

print("progress: url token round-trips, seeds the app, and fails safe")


# The sidebar is the only route to the Ask view, and it shipped unreachable:
# `stExpandSidebarButton` is a child of `stToolbar`, so a rule hiding the toolbar
# hides the control that opens a collapsed sidebar. On Streamlit Cloud the
# sidebar loads collapsed, so the deployed app had no navigation at all while
# localhost — where it loads expanded — looked perfect. Neither half is visible
# to a test that only calls functions, so both are asserted on the source.
import re as _re  # noqa: E402

from streamlit_app import CSS  # noqa: E402

app_src = (ROOT / "streamlit_app.py").read_text()
# Comments first — this check exists because of a rule whose comment now names
# the very selectors it must not find, and matching prose would fail forever.
_css = _re.sub(r"/\*.*?\*/", "", CSS, flags=_re.S)
hidden = {
    sel.strip()
    for rule in _re.findall(r"([^{}]*)\{[^{}]*display\s*:\s*none[^{}]*\}", _css)
    for sel in rule.split(",")
}
ok("no CSS rule hides the toolbar, which owns the sidebar's expand button",
   not any("stToolbar" in s for s in hidden),
   str([s for s in hidden if "stToolbar" in s]))
ok("no CSS rule hides the sidebar or its expand button",
   not any("Sidebar" in s for s in hidden), str([s for s in hidden if "Sidebar" in s]))
ok("the sidebar is opened explicitly rather than left on auto",
   'initial_sidebar_state="expanded"' in app_src)

# The number lookup is the thing people actually type. Every spelling of it has
# to reach the same trace, and a number outside the corpus has to say so rather
# than guess a neighbour.
lookups = {"1": "two-sum", "25": "reverse-nodes-in-k-group", "leetcode 25": "reverse-nodes-in-k-group",
           "lc 25": "reverse-nodes-in-k-group", "#25": "reverse-nodes-in-k-group",
           "217": "contains-duplicate", "226": "invert-binary-tree"}
for query, want in lookups.items():
    got, _ = resolve(query, index["problems"])
    ok(f"{query!r} resolves to {want}", got == want, f"got {got}")
ok("a number outside the corpus resolves to nothing, not a neighbour",
   resolve("9999", index["problems"])[0] is None)
print(f"ask: {len(lookups)} number spellings resolve; sidebar reachable")


# A failed generation used to print one sentence of advice whatever went wrong,
# so a rejected key told the reader to go and pick a stronger model.
import urllib.error as _ue  # noqa: E402

from streamlit_app import _CHAT_SYSTEM, failure_advice  # noqa: E402

_http = lambda c: _ue.HTTPError("u", c, "boom", {}, None)
ok("a 403 is named as a credential problem",
   "credential problem" in failure_advice(_http(403)), failure_advice(_http(403))[:60])
ok("a 403 does not send the reader off to change the model",
   "stronger" not in failure_advice(_http(403)))
ok("a 401 reads the same way", "credential problem" in failure_advice(_http(401)))
ok("a 429 is named as a rate limit", "Rate-limited" in failure_advice(_http(429)))
ok("a 502 is named as the provider's outage",
   "outage" in failure_advice(_http(502)), failure_advice(_http(502))[:60])
ok("a trace that will not replay still gets the model advice",
   "stronger" in failure_advice(ValueError("ops and result disagree")))

# The message is markdown, and an escaped backslash in an ordinary string is a
# literal backslash-n that renders as text rather than a break — which is how it
# shipped, visible in the app as "Forbidden\n\nA trace that will not replay".
# The source legitimately contains a real "\n" escape, so what makes this
# detectable is the doubled backslash, not the n.
ok("the failure message uses a real newline, not an escaped backslash",
   "\\\\n" not in app_src, repr([l for l in app_src.splitlines() if "\\\\n" in l][:2]))

# Which title a LeetCode number maps to is a lookup, and the model is not a copy
# of it: asked about 2135 with no grounding it explained a different problem.
ok("the chat prompt forbids recalling a number from memory",
   "cannot reliably recall which problem a LeetCode number" in _CHAT_SYSTEM)
unknown_reply = resolve("leetcode 2135", index["problems"])[1]
ok("a number outside the corpus still produces a fact to ground on",
   unknown_reply.startswith("I do not have LeetCode 2135"), unknown_reply[:60])
ok("that fact is not one of the reader-only nudges the prompt drops",
   not unknown_reply.startswith(("Ask for a problem", "No match.")))
print("ask: failure advice matches the failure; numbers are grounded, not recalled")


# "trace t" would have spent a 30-60s generation on one character. The budget
# gates count what was spent; this is about not spending it on a keystroke.
from streamlit_app import MIN_TRACE_CHARS  # noqa: E402

ok("a stray keystroke is below the trace floor", len("t") < MIN_TRACE_CHARS)
ok("the shortest real problem names clear it",
   all(len(n) >= MIN_TRACE_CHARS for n in ["wiggle sort", "jump game", "word break"]))
ok("the floor is checked before the budget is claimed",
   app_src.index("MIN_TRACE_CHARS:") < app_src.index('elif not budget("gen")'))
print(f"ask: trace floor is {MIN_TRACE_CHARS} chars, checked before spending")

# Retiring a provider empties the chain, which is the same shape as never having
# configured one — so a refused key reported itself as a missing setting and sent
# the reader to the setup block to fix something that was already right.
from streamlit_app import retired  # noqa: E402

_gen_mod = sys.modules.get("_gen")
ok("nothing is retired on a clean run", retired() == {}, str(retired()))
if _gen_mod is not None:
    _gen_mod._DEAD["nvidia"] = "http_403"
    try:
        ok("a refused key is reported as retired, not as unconfigured",
           retired() == {"nvidia": "http_403"}, str(retired()))
    finally:
        _gen_mod._DEAD.clear()
    ok("clearing it restores the unconfigured case", retired() == {})
print("ask: a refused key reads as a credential problem, not a missing setting")

for f in fails:
    print("  FAIL", f)
if fails:
    sys.exit(1)
print("streamlit reader: ok")
