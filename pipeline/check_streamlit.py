"""Replay every committed trace through the Streamlit reader.

`streamlit_app.py` re-implements `lib/fold.ts` in Python. Two readers of the same
artifacts is exactly the kind of thing that drifts silently, so this walks every
step of every variant of every trace: the fold must not dangle a path, the step
line must index into the source, and the renderer must survive every shape the
corpus contains.

    python3 pipeline/check_streamlit.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

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

print(f"ask box: {len(cases) + 1} queries")


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

print("app: 11 interactions")
for f in fails:
    print("  FAIL", f)
if fails:
    sys.exit(1)
print("streamlit reader: ok")
