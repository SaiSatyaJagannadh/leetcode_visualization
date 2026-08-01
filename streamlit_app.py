"""LeetViz on Streamlit.

The Next.js app is the primary front end; this is a second reader over the same
committed artifacts. It reads `traces/*.json` directly — no Python tracing here,
no server, no API. Ops are folded forward exactly the way `lib/fold.ts` does it,
so a step shown here is the step the React player shows.
"""

import difflib
import html
import json
import re
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent
TRACES = ROOT / "traces"


# ---------------------------------------------------------------- data

@st.cache_data
def load_index():
    return json.loads((TRACES / "index.json").read_text())


@st.cache_data
def load_trace(slug):
    return json.loads((TRACES / f"{slug}.json").read_text())


def state_at(steps, index):
    """State after `index` steps. Replays from 0 — same contract as stateAt()."""
    state = {}
    for step in steps[: index + 1]:
        for op in step["ops"]:
            path = op[1]
            node = state
            for key in path[:-1]:
                node = node[key]
            if op[0] == "del":
                node.pop(path[-1], None)
            else:
                node[path[-1]] = json.loads(json.dumps(op[2]))
    return state


def touched(step):
    return {str(op[1][0]) for op in step["ops"]}


def attachments(viz, host):
    """Vars attached to `host`, as {role: [varname, ...]} — `pointer:nums` etc."""
    out = {}
    for name, spec in viz.items():
        if ":" in spec:
            role, target = spec.split(":", 1)
            if target == host:
                out.setdefault(role, []).append(name)
    return out


def deref(val, nodes):
    return nodes.get(val["$ref"]) if isinstance(val, dict) and "$ref" in val else None


# ---------------------------------------------------------------- rendering

# The palette is app/globals.css, so the two front ends read as one product.
BG, PANEL, LINE, FG, DIM, ACCENT, HOT = (
    "#0e1116", "#161b22", "#262d38", "#e6edf3", "#8b949e", "#58a6ff", "#f0883e",
)

CSS = f"""
<style>
.lv-src {{ font: 13px/1.6 ui-monospace, SFMono-Regular, Menlo, monospace;
          border:1px solid {LINE}; border-radius:10px; background:{PANEL};
          padding:6px 0; overflow-x:auto; color:{FG}; }}
.lv-src div {{ padding:1px 14px; white-space:pre; }}
.lv-src div.on {{ background:#1b2836; box-shadow:inset 3px 0 0 {ACCENT}; }}
.lv-note {{ border:1px solid {LINE}; border-left:3px solid {HOT}; border-radius:10px;
           padding:12px 16px; margin:12px 0; background:{PANEL}; color:{FG};
           font-size:14px; }}
.lv-cells {{ display:flex; flex-wrap:wrap; gap:5px; margin:2px 0 12px; }}
.lv-cell {{ min-width:40px; text-align:center; border:1px solid {LINE};
           border-radius:7px; padding:5px 8px; background:{PANEL}; color:{FG};
           font:13px ui-monospace, monospace; }}
.lv-cell.mark {{ border-color:{HOT}; color:{HOT}; background:#f0883e14; }}
.lv-idx {{ font-size:10px; color:{DIM}; background:none !important; }}
.lv-ptr {{ font-size:11px; color:{HOT}; height:15px; background:none !important; }}
.lv-name {{ font:12px ui-monospace, monospace; color:{DIM}; margin-top:8px; }}
.lv-name b {{ color:{FG}; }}
.lv-grid {{ border-collapse:separate; border-spacing:4px; margin:2px 0 12px; }}
.lv-grid td {{ border:1px solid {LINE}; border-radius:7px; padding:5px 10px;
              text-align:center; background:{PANEL}; color:{FG};
              font:13px ui-monospace, monospace; }}
.lv-grid td.mark {{ border-color:{HOT}; color:{HOT}; background:#f0883e14; }}
.lv-ret {{ display:inline-block; border:1px solid #2b4d75; border-radius:999px;
          padding:4px 12px; margin-top:10px; color:{ACCENT}; background:#58a6ff14;
          font:13px ui-monospace, monospace; }}
.lv-note.quiet {{ color:{DIM}; border-left-color:{LINE}; }}
.lv-count {{ text-align:right; color:{DIM}; font:13px ui-monospace, monospace;
            padding-top:6px; }}

/* header, NeetCode-style: title, then difficulty and pattern as pills */
.lv-brand {{ font-size:20px; font-weight:650; letter-spacing:-0.02em; color:{FG}; }}
.lv-title {{ font-size:30px; font-weight:650; letter-spacing:-0.02em;
            color:{FG}; margin-bottom:12px; }}
.lv-pill {{ display:inline-block; padding:3px 11px; margin:0 7px 8px 0;
           border:1px solid {LINE}; border-radius:999px; color:{DIM}; font-size:13px; }}
.lv-pill.Easy {{ color:#3fb950; border-color:#1f4a2c; }}
.lv-pill.Medium {{ color:{HOT}; border-color:#5a3a1a; }}
.lv-pill.Hard {{ color:#f85149; border-color:#5a1f22; }}
a.lv-pill.link {{ color:{ACCENT}; border-color:#2b4d75; text-decoration:none; }}
a.lv-pill.link:hover {{ background:#58a6ff14; border-color:{ACCENT}; }}
.lv-prompt {{ color:{DIM}; max-width:78ch; margin:10px 0 18px; }}
.lv-cx {{ color:{DIM}; font:12px ui-monospace, monospace; margin:2px 0 10px; }}
.lv-eg {{ border:1px solid {LINE}; border-radius:10px; background:{PANEL};
         padding:12px 16px; margin-bottom:10px; font:13px ui-monospace, monospace;
         color:{FG}; }}
.lv-eg span {{ color:{DIM}; }}
.lv-eg .why {{ color:{DIM}; font-family:inherit; margin-top:6px; }}
.lv-ask {{ color:{ACCENT}; font-size:13px; margin-top:14px; }}
.lv-ask::before {{ content:"› "; color:{DIM}; }}

/* the transport row: square, quiet buttons rather than Streamlit's wide default */
div[data-testid="stHorizontalBlock"] button[kind="secondary"] {{
  min-height:34px; padding:2px 0; border-color:{LINE}; background:{PANEL};
  color:{FG};
}}
div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {{
  border-color:{ACCENT}; color:{ACCENT};
}}
</style>
"""


def source_html(lines, current):
    rows = "".join(
        f'<div class="{"on" if i == current else ""}">{html.escape(line) or "&nbsp;"}</div>'
        for i, line in enumerate(lines)
    )
    return f'<div class="lv-src">{rows}</div>'


def cells_html(name, values, marks, pointers):
    """One-dimensional sequence: index rulers above, pointer labels below."""
    cells, idx, ptr = [], [], []
    for i, v in enumerate(values):
        hit = "mark" if i in marks else ""
        cells.append(f'<div class="lv-cell {hit}">{html.escape(str(v))}</div>')
        idx.append(f'<div class="lv-cell lv-idx" style="border:none">{i}</div>')
        names = " ".join(pointers.get(i, []))
        ptr.append(f'<div class="lv-cell lv-ptr" style="border:none">{html.escape(names)}</div>')
    body = (
        f'<div class="lv-cells">{"".join(idx)}</div>'
        f'<div class="lv-cells">{"".join(cells)}</div>'
    )
    if any(pointers.values()):
        body += f'<div class="lv-cells">{"".join(ptr)}</div>'
    return f'<div class="lv-name"><b>{html.escape(name)}</b></div>{body}'


def grid_html(name, rows, marks):
    body = "".join(
        "<tr>"
        + "".join(
            f'<td class="{"mark" if (r, c) in marks else ""}">{html.escape(str(v))}</td>'
            for c, v in enumerate(row)
        )
        + "</tr>"
        for r, row in enumerate(rows)
    )
    return (
        f'<div class="lv-name"><b>{html.escape(name)}</b></div>'
        f'<table class="lv-grid">{body}</table>'
    )


def svg(shapes, width, height):
    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" '
        f'style="max-width:{width}px;height:auto;font:12px ui-monospace,monospace">'
        + "".join(shapes)
        + "</svg>"
    )


def nodes_svg(nodes, labels):
    """Trees and linked lists: `at` coordinates were baked by tracer/structs.py."""
    if not nodes:
        return ""
    sx, sy, pad, r = 62, 66, 34, 17
    pos = {nid: (n.get("at") or [0, 0]) for nid, n in nodes.items()}
    # The tracer scopes $nodes to what the current frame can reach, so a deep
    # subtree keeps its original coordinates. Shift back to the origin or it
    # draws in a corner of a mostly empty canvas.
    ox = min(x for x, _ in pos.values())
    oy = min(y for _, y in pos.values())
    px = {nid: ((x - ox) * sx + pad, (y - oy) * sy + pad) for nid, (x, y) in pos.items()}
    edges, circles = [], []
    for nid, node in nodes.items():
        x0, y0 = px[nid]
        for key, val in node.items():
            child = val.get("$ref") if isinstance(val, dict) else None
            if child in px:
                x1, y1 = px[child]
                edges.append(
                    f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" '
                    f'stroke="{LINE}" stroke-width="1.5" />'
                )
        tags = labels.get(nid, [])
        fill = "#58a6ff26" if tags else PANEL
        circles.append(
            f'<circle cx="{x0}" cy="{y0}" r="{r}" fill="{fill}" '
            f'stroke="{ACCENT if tags else LINE}" />'
            f'<text x="{x0}" y="{y0 + 4}" text-anchor="middle" fill="{FG}">'
            f'{html.escape(str(node.get("val")))}</text>'
        )
        if tags:
            circles.append(
                f'<text x="{x0}" y="{y0 - r - 6}" text-anchor="middle" fill="{ACCENT}">'
                f'{html.escape(" ".join(tags))}</text>'
            )
    w = max(x for x, _ in px.values()) + pad + r
    h = max(y for _, y in px.values()) + pad + r
    return svg(edges + circles, w, h)


def calls_svg(calls):
    """The recursion call tree, keyed the same way $nodes is."""
    if not calls:
        return ""
    sx, sy, pad = 150, 46, 20
    at = {cid: (c.get("at") or [0, 0]) for cid, c in calls.items()}
    ox = min(x for x, _ in at.values())
    oy = min(y for _, y in at.values())
    px = {cid: ((x - ox) * sx + pad, (y - oy) * sy + pad) for cid, (x, y) in at.items()}
    parts = []
    for cid, c in calls.items():
        x0, y0 = px[cid]
        parent = c.get("parent")
        if parent in px:
            x1, y1 = px[parent]
            parts.append(
                f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1 + 10}" '
                f'stroke="{LINE}" stroke-width="1.5" />'
            )
        done = c.get("status") != "active"
        args = ", ".join(f"{k}={v}" for k, v in (c.get("args") or {}).items())
        text = f'{c.get("fn")}({args})'
        if done and c.get("ret") is not None:
            text += f' → {c["ret"]}'
        parts.append(
            f'<rect x="{x0}" y="{y0 - 12}" width="{sx - 14}" height="24" rx="6" '
            f'fill="{PANEL if done else "#58a6ff26"}" '
            f'stroke="{LINE if done else ACCENT}" />'
            f'<text x="{x0 + 8}" y="{y0 + 4}" fill="{DIM if done else FG}">'
            f'{html.escape(text[:22])}</text>'
        )
    w = max(x for x, _ in px.values()) + sx
    h = max(y for _, y in px.values()) + pad + 16
    return svg(parts, w, h)


def graph_svg(adj, coords, labels, marked):
    """Adjacency plus the circle layout baked into approach.layout."""
    keys = list(adj) if isinstance(adj, dict) else list(range(len(adj)))
    if not coords:
        return ""
    r, pad = 130, 46
    px = {}
    for k in keys:
        c = coords.get(str(k))
        if c:
            px[str(k)] = (c[0] * r + r + pad, c[1] * r + r + pad)
    edges, circles = [], []
    for k in keys:
        a = px.get(str(k))
        if not a:
            continue
        for n in adj[k] if isinstance(adj, dict) else adj[k]:
            b = px.get(str(n))
            if b:
                edges.append(
                    f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" '
                    f'stroke="{LINE}" stroke-width="1.5" />'
                )
    for k in keys:
        a = px.get(str(k))
        if not a:
            continue
        hot = str(k) in marked
        circles.append(
            f'<circle cx="{a[0]}" cy="{a[1]}" r="19" '
            f'fill="{"#f0883e26" if hot else PANEL}" '
            f'stroke="{HOT if hot else LINE}" />'
            f'<text x="{a[0]}" y="{a[1] + 4}" text-anchor="middle" fill="{FG}">'
            f'{html.escape(str(k))}</text>'
        )
        tag = labels.get(str(k))
        if tag is not None:
            circles.append(
                f'<text x="{a[0]}" y="{a[1] - 25}" text-anchor="middle" fill="{HOT}">'
                f'{html.escape(str(tag))}</text>'
            )
    size = 2 * (r + pad)
    return svg(edges + circles, size, size)


def coord_pairs(val, out):
    """Every [row, col] pair buried anywhere in a `cells:` var."""
    if isinstance(val, list):
        if len(val) == 2 and all(isinstance(v, int) for v in val):
            out.add((val[0], val[1]))
        else:
            for item in val:
                coord_pairs(item, out)
    elif isinstance(val, dict):
        for item in val.values():
            coord_pairs(item, out)


def render_state(state, viz, layout, changed):
    nodes = state.get("$nodes") or {}
    calls = state.get("$calls") or {}
    attached = {n for n, spec in viz.items() if ":" in spec}
    parts = []

    # Node-shaped vars all live in one diagram; the variables just label it.
    labels = {}
    for name, val in state.items():
        target = deref(val, nodes)
        if target is not None:
            labels.setdefault(val["$ref"], []).append(name)
    if nodes:
        parts.append(nodes_svg(nodes, labels))
    if calls:
        parts.append(calls_svg(calls))

    for name, val in state.items():
        if name.startswith("$") or name in attached or deref(val, nodes) is not None:
            continue
        kind = viz.get(name, "")
        hooks = attachments(viz, name)

        if kind == "graph":
            marked = set()
            for m in hooks.get("marked", []):
                marked |= {str(x) for x in (state.get(m) or [])}
            tags = {}
            for l in hooks.get("labels", []):
                src = state.get(l)
                if isinstance(src, dict):
                    tags.update({str(k): v for k, v in src.items()})
                elif isinstance(src, list):
                    tags.update({str(i): v for i, v in enumerate(src)})
            parts.append(graph_svg(val, layout.get(name, {}), tags, marked))
            continue

        is_grid = isinstance(val, list) and val and all(isinstance(r, list) for r in val)
        if kind == "grid" or is_grid:
            marks = set()
            for c in hooks.get("cells", []):
                coord_pairs(state.get(c), marks)
            for r in hooks.get("row", []):
                if isinstance(state.get(r), int):
                    marks |= {(state[r], c) for c in range(len(val[0]))}
            parts.append(grid_html(name, val, marks))
            continue

        if isinstance(val, list):
            pointers, marks = {}, set()
            for role in ("pointer", "index"):
                for p in hooks.get(role, []):
                    i = state.get(p)
                    if isinstance(i, int) and 0 <= i < len(val):
                        pointers.setdefault(i, []).append(p)
                        marks.add(i)
            parts.append(cells_html(name, val, marks, pointers))
            continue

        hot = " ←" if name in changed else ""
        shown = json.dumps(val) if isinstance(val, dict) else str(val)
        parts.append(
            f'<div class="lv-name"><b>{html.escape(name)}</b> = '
            f'{html.escape(shown)}{hot}</div>'
        )
    return "".join(p for p in parts if p)


# ---------------------------------------------------------------- ask

def resolve(query, problems):
    """Turn "leetcode 25" / "25" / "two sum" / "sliding window" into a slug.

    Returns (slug_or_None, reply). The corpus is fixed at 150 problems, so this
    is lookup, not generation — it answers instantly and costs nothing.
    """
    q = query.strip().lower()
    if not q:
        return None, "Ask for a problem by number, name, or pattern."

    ready = [p for p in problems if p["ready"]]

    # A bare number, or one after "leetcode"/"lc"/"#", means the LeetCode number.
    nums = re.findall(r"\d+", q)
    if nums:
        n = int(nums[0])
        for p in ready:
            if p["leetcode"] == n:
                return p["slug"], (
                    f'LeetCode {n} is **{p["title"]}** — {p["difficulty"]}, '
                    f'{p["pattern"]}. Loaded above: press play to watch it run.'
                )
        missing = next((p for p in problems if p["leetcode"] == n), None)
        if missing:
            return None, (
                f'LeetCode {n} is **{missing["title"]}**, which is on the roadmap '
                "but has no trace yet."
            )
        return None, (
            f"I do not have LeetCode {n}. These 150 are the NeetCode 150 — for "
            "anything else, the Next.js site can generate a trace at `/solve`."
        )

    # Exact title, then exact pattern. Pattern comes before the substring pass
    # below or "sliding window" would land on Sliding Window Maximum, the only
    # title containing those words, instead of listing the pattern.
    for p in ready:
        if q == p["title"].lower() or q == p["slug"]:
            return p["slug"], f'**{p["title"]}** — {p["difficulty"]}, {p["pattern"]}.'
    exact_pattern = [x for x in {p["pattern"] for p in ready} if q == x.lower()]
    subs = [p for p in ready if q in p["title"].lower()]
    if len(subs) == 1 and not exact_pattern:
        return subs[0]["slug"], f'**{subs[0]["title"]}** — {subs[0]["pattern"]}.'

    # A pattern name lists its problems rather than guessing one of them.
    pats = exact_pattern or [x for x in {p["pattern"] for p in ready} if q in x.lower()]
    if len(pats) == 1:
        named = [p for p in ready if p["pattern"] == pats[0]]
        listed = ", ".join(f'{p["leetcode"]}. {p["title"]}' for p in named[:12])
        return None, f"**{pats[0]}** has {len(named)} traced: {listed}."

    if subs:
        listed = ", ".join(f'{p["leetcode"]}. {p["title"]}' for p in subs[:8])
        return None, f"{len(subs)} match that: {listed}. Which one?"

    close = difflib.get_close_matches(q, [p["title"].lower() for p in ready], 3, 0.6)
    if close:
        hit = next(p for p in ready if p["title"].lower() == close[0])
        return hit["slug"], f'Closest match: **{hit["title"]}** — {hit["pattern"]}.'
    return None, "No match. Try a LeetCode number, a title, or a pattern name."


# ---------------------------------------------------------------- player

TICK = 0.75  # seconds per step when playing, matching the React player's 650ms


def _seek(key, to, last):
    st.session_state[key] = max(0, min(to, last))
    st.session_state.playing = False


def _nudge(key, delta, last):
    _seek(key, st.session_state.get(key, 0) + delta, last)


def _toggle(key, last):
    # Pressing play on the last step replays from the top, the way a video does.
    if not st.session_state.playing and st.session_state.get(key, 0) >= last:
        st.session_state[key] = 0
    st.session_state.playing = not st.session_state.playing


def stage(approach, variant, skey):
    """Code, state, narration and transport. Re-runs on its own while playing."""
    steps = variant["steps"]
    last = len(steps) - 1

    # Advance before any widget is drawn — Streamlit forbids writing a widget's
    # key after that widget exists, and the slider below reads this one.
    if st.session_state.playing:
        cur = min(st.session_state.get(skey, 0), last)
        if cur >= last:
            st.session_state.playing = False
            st.rerun(scope="app")  # drop the timer, otherwise it keeps ticking
        st.session_state[skey] = cur + 1

    i = min(st.session_state.get(skey, 0), last)
    step = steps[i]

    left, right = st.columns([1, 1], gap="medium")
    with left:
        st.markdown(source_html(approach["source"], step["line"]), unsafe_allow_html=True)
    with right:
        st.markdown(
            render_state(state_at(steps, i), approach["viz"], approach["layout"], touched(step)),
            unsafe_allow_html=True,
        )
        if i == last:
            st.markdown(
                f'<div class="lv-ret">return {html.escape(json.dumps(variant["result"]))}</div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        f'<div class="lv-note{"" if step.get("note") else " quiet"}">'
        f'{html.escape(step.get("note") or "…")}</div>',
        unsafe_allow_html=True,
    )

    bar = st.columns([1, 1, 1, 1, 1, 14, 3])
    playing = st.session_state.playing
    for col, label, help_, cb, args in (
        (bar[0], "⏮", "First step", _seek, (skey, 0, last)),
        (bar[1], "◀", "Previous step", _nudge, (skey, -1, last)),
        (bar[2], "⏸" if playing else "▶", "Pause" if playing else "Play", _toggle, (skey, last)),
        (bar[3], "▶", "Next step", _nudge, (skey, 1, last)),
        (bar[4], "⏭", "Last step", _seek, (skey, last, last)),
    ):
        col.button(label, help=help_, on_click=cb, args=args, key=f"{skey}:{help_}")
    bar[5].slider("Step", 0, last, key=skey, label_visibility="collapsed")
    bar[6].markdown(f'<div class="lv-count">{i + 1} / {last + 1}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- page


def pill(text, kind=""):
    return f'<span class="lv-pill {kind}">{html.escape(text)}</span>'


def pick(what, options, scope):
    """A tab strip that renders one option, not all of them. Returns the choice."""
    labels = [o["label"] for o in options]
    key = f"{what}:{scope}"
    chosen = st.segmented_control(
        what, labels, default=labels[0], key=key, label_visibility="collapsed"
    )
    return options[labels.index(chosen)] if chosen in labels else options[0]


def main():
    st.set_page_config(page_title="LeetViz", page_icon="◆", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)

    index = load_index()
    problems = index["problems"]
    ready = [p for p in problems if p["ready"]]
    st.session_state.setdefault("slug", ready[0]["slug"])
    st.session_state.setdefault("playing", False)
    st.session_state.setdefault("chat", [])

    # Docked at the bottom of the view wherever it is called, so handling it
    # first means a resolved problem renders on this run rather than the next.
    asked = st.chat_input("Ask for a problem — “leetcode 25”, “two sum”, “sliding window”")
    if asked:
        slug, reply = resolve(asked, problems)
        st.session_state.chat = [(asked, reply)] + st.session_state.chat[:4]
        if slug:
            st.session_state.slug = slug
            st.session_state.pattern = "All"  # or the picker would not list it
            st.session_state.playing = False

    with st.sidebar:
        st.markdown('<div class="lv-brand">LeetViz</div>', unsafe_allow_html=True)
        st.caption(f"{len(ready)} problems traced line by line, replayed from JSON")
        patterns = ["All"] + [x for x in index["patterns"] if any(p["pattern"] == x for p in ready)]
        st.session_state.setdefault("pattern", "All")
        pattern = st.selectbox("Pattern", patterns, key="pattern")
        pool = [p for p in ready if pattern == "All" or p["pattern"] == pattern]
        if st.session_state.slug not in {p["slug"] for p in pool}:
            st.session_state.slug = pool[0]["slug"]
        by_slug = {p["slug"]: p for p in pool}
        st.selectbox(
            "Problem",
            list(by_slug),
            key="slug",
            format_func=lambda s: f'{by_slug[s]["leetcode"]}. {by_slug[s]["title"]}',
        )
        for q, reply in st.session_state.chat:
            st.markdown(f'<div class="lv-ask">{html.escape(q)}</div>', unsafe_allow_html=True)
            st.markdown(reply)

    choice = next(p for p in problems if p["slug"] == st.session_state.slug)
    trace = load_trace(choice["slug"])

    st.markdown(f'<div class="lv-title">{html.escape(trace["title"])}</div>', unsafe_allow_html=True)
    tags = pill(trace.get("difficulty", ""), trace.get("difficulty", "")) + pill(trace["pattern"])
    st.markdown(
        tags
        + f'<a class="lv-pill link" target="_blank" rel="noopener noreferrer" '
        f'href="https://leetcode.com/problems/{choice["lc"]}/">LeetCode '
        f'{trace.get("leetcode", "")} ↗</a>'
        + f'<a class="lv-pill link" target="_blank" rel="noopener noreferrer" '
        f'href="https://neetcode.io/problems/{choice["lc"]}">NeetCode ↗</a>',
        unsafe_allow_html=True,
    )
    if trace.get("prompt"):
        st.markdown(f'<p class="lv-prompt">{html.escape(trace["prompt"])}</p>',
                    unsafe_allow_html=True)

    if trace.get("examples") or trace.get("constraints"):
        with st.expander("Examples and constraints"):
            for ex in trace.get("examples", []):
                st.markdown(
                    f'<div class="lv-eg"><span>in </span>{html.escape(ex["input"])}<br>'
                    f'<span>out </span>{html.escape(ex["output"])}'
                    + (f'<div class="why">{html.escape(ex["why"])}</div>' if ex.get("why") else "")
                    + "</div>",
                    unsafe_allow_html=True,
                )
            for c in trace.get("constraints", []):
                st.markdown(f"- {c}")

    # Deliberately not st.tabs: tabs render every approach on every run, so each
    # one would build a fragment from the same function and they would collide —
    # the auto-rerun timer then never fires. One picker, one stage, one fragment.
    approach = pick("approach", trace["approaches"], choice["slug"])
    st.markdown(
        f'<div class="lv-cx">time {approach["complexity"]["time"]} · '
        f'space {approach["complexity"]["space"]}</div>',
        unsafe_allow_html=True,
    )
    variant = pick("variant", approach["variants"], f'{choice["slug"]}:{approach["id"]}')
    skey = f'{choice["slug"]}:{approach["id"]}:{variant["id"]}'
    # run_every is read when the decorator is applied, so applying it per run is
    # what lets play and pause actually start and stop the timer.
    st.fragment(run_every=TICK if st.session_state.playing else None)(stage)(
        approach, variant, skey
    )
    st.caption("Press ▶ to watch it run. Every step is the real traced state, not an animation.")


if __name__ == "__main__":
    main()
