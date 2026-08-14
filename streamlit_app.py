"""LeetViz on Streamlit.

The Next.js app is the primary front end; this is a second reader over the same
committed artifacts. It reads `traces/*.json` directly — no Python tracing here,
no server, no API. Ops are folded forward exactly the way `lib/fold.ts` does it,
so a step shown here is the step the React player shows.
"""

import base64
import difflib
import hashlib
import html
import json
import os
import re
import sys
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


# ---------------------------------------------------------------- progress
#
# Which problems you have watched is the one piece of state worth outliving the
# tab, and it was dying on every refresh — a study tool that reads 0 / 150 every
# visit is not measuring anything.
#
# It lives in the URL rather than on the server because Streamlit cannot set a
# cookie: `st.context.cookies` is read-only, so there is no per-visitor id to key
# storage on, and the alternatives are a third-party JS component or hashing the
# IP. Hashing the IP would put everyone behind one office router on the same
# progress bar, which is worse than forgetting.
#
# What that buys, and what it costs: a refresh, a bookmark and a restored tab all
# keep their ticks, and the URL is portable — paste it on your phone and your
# progress goes with it. A cold visit to the bare domain starts empty. That is
# the real ceiling of this approach, not an oversight.


@st.cache_data
def all_slugs():
    """Sorted, so a bit position depends on the corpus and not on display order."""
    return sorted(p["slug"] for p in load_index()["problems"])


def _fingerprint(slugs):
    """Four characters naming this exact corpus.

    A bitmask is only meaningful against the list it was minted for. Add a
    problem and every bit after it shifts by one, so an old token would tick the
    wrong rows — confidently, and with no way for the reader to tell. The
    fingerprint makes that case detectable, and a mismatch costs someone their
    ticks rather than showing them somebody else's.
    """
    return hashlib.sha256("\x00".join(slugs).encode()).hexdigest()[:4]


def encode_seen(seen, slugs):
    """The watched set as a fingerprinted bitmask, short enough to live in a URL.

    150 problems is 150 bits — 19 bytes, 26 characters once base64'd. Listing the
    slugs instead would be a 2 KB query string.
    """
    bits = bytearray((len(slugs) + 7) // 8)
    for i, slug in enumerate(slugs):
        if slug in seen:
            bits[i // 8] |= 1 << (i % 8)
    packed = base64.urlsafe_b64encode(bytes(bits)).decode().rstrip("=")
    return _fingerprint(slugs) + packed


def decode_seen(token, slugs):
    """Inverse of encode_seen. Anything malformed reads as "watched nothing".

    The token is a query parameter, so it is whatever the caller typed. A progress
    bar is not worth an exception on page load, and a missing tick is a smaller
    lie than a wrong one — every failure here fails to empty.
    """
    if not token or token[:4] != _fingerprint(slugs):
        return set()
    body = token[4:]
    try:
        bits = base64.urlsafe_b64decode(body + "=" * (-len(body) % 4))
    except ValueError:  # binascii.Error subclasses it; bad padding, bad alphabet
        return set()
    return {
        slug for i, slug in enumerate(slugs)
        if i // 8 < len(bits) and bits[i // 8] >> (i % 8) & 1
    }


def watch(slug):
    """Mark a problem watched.

    The only place `seen` grows, which is what makes it the only place the URL
    has to be kept in step. Both callers used to do the `add` themselves, and a
    third one would have quietly not persisted.
    """
    st.session_state.seen.add(slug)
    st.query_params["p"] = encode_seen(st.session_state.seen, all_slugs())


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

/* The transport row and the roadmap rows are both plain st.buttons inside
   horizontal blocks, so they are told apart by key: since 1.39 a widget's key
   becomes an `st-key-<key>` class on its container. Styling by data-testid
   alone would make every roadmap row look like a transport button. */
div[class*="st-key-tp_"] button {{
  min-height:34px; padding:2px 0; border-color:{LINE}; background:{PANEL};
  color:{FG};
}}
div[class*="st-key-tp_"] button:hover {{ border-color:{ACCENT}; color:{ACCENT}; }}

/* the roadmap: NeetCode's grouped problem table */
.lv-sec {{ display:flex; align-items:center; gap:12px; margin:26px 0 2px; }}
.lv-sec b {{ font-size:17px; font-weight:620; color:{FG}; letter-spacing:-0.01em; }}
.lv-sec span {{ font:12px ui-monospace, monospace; color:{DIM}; }}
.lv-bar {{ flex:0 0 90px; height:4px; border-radius:999px; background:{LINE};
          overflow:hidden; }}
.lv-bar i {{ display:block; height:100%; background:{ACCENT}; }}
/* line-height matches the row button's height, so the number, the title and
   the tick sit on one line rather than three slightly different ones */
.lv-num {{ font:12px/30px ui-monospace, monospace; color:{DIM}; text-align:right; }}
/* the pill carries bottom margin for the header stacks; in a row it must not */
.lv-rowcell .lv-pill {{ margin:0; }}
.lv-seen {{ color:#3fb950; font:13px/30px sans-serif; text-align:center; }}
.lv-head {{ border-bottom:1px solid {LINE}; margin:0 0 2px; padding-bottom:6px;
           font:11px ui-monospace, monospace; color:{DIM};
           text-transform:uppercase; letter-spacing:0.08em; }}

/* A roadmap row: a full-width button that reads as a table row, not a control.
   The label sits in a nested flex div, so left-aligning the button is not
   enough — the inner div is what centres it. */
div[class*="st-key-go_"] button {{
  border:none; background:none; padding:4px 6px; min-height:0; color:{FG};
}}
div[class*="st-key-go_"] button > div {{ width:100%; justify-content:flex-start; }}
div[class*="st-key-go_"] button p {{ font-size:14px; font-weight:400; }}
div[class*="st-key-go_"] button:hover {{ background:{PANEL}; color:{ACCENT}; }}
div[class*="st-key-go_"] button:focus {{ color:{ACCENT}; box-shadow:none; }}

/* Rows are separate horizontal blocks, so the gap between them is Streamlit's
   1rem element spacing. :has() picks out only the rows, leaving every other
   block on the page at its normal rhythm. */
div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-go_"]) {{
  border-bottom:1px solid #1a2029; margin-bottom:-10px; padding-bottom:2px;
}}
div[data-testid="stHorizontalBlock"]:has(div[class*="st-key-go_"]):hover {{
  border-color:{LINE};
}}

/* Streamlit's own chrome on a link people are handed. Hide the Deploy button by
   name, NOT the whole toolbar: stExpandSidebarButton is a child of stToolbar, and
   on Streamlit Cloud the sidebar loads collapsed. Hiding the toolbar there left a
   collapsed sidebar with no way to open it — which is the whole navigation, so
   the Ask view became unreachable on the deployed app while looking fine locally,
   where the sidebar happens to load expanded. There is no Deploy button on Cloud
   at all, so the broad rule bought nothing and cost everything. */
[data-testid="stAppDeployButton"], [data-testid="stDecoration"], footer {{ display:none; }}
div[data-testid="stMainBlockContainer"] {{ padding-top:3rem; }}

/* back / prev / next read as links, the way NeetCode's problem nav does */
div[class*="st-key-nav_"] button {{
  border:none; background:none; padding:2px 6px; min-height:0; color:{DIM};
}}
div[class*="st-key-nav_"] button:hover {{ color:{ACCENT}; background:none; }}
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

        # `viz` is a declaration, and a generated trace can declare `grid` on a
        # flat list — gemini just did. Honour it only when the value really has
        # rows, or grid_html iterates an int and takes the whole page down with
        # it. A committed trace never hits this; a generated one is not trusted.
        has_rows = isinstance(val, list) and val and all(isinstance(r, (list, str)) for r in val)
        is_grid = has_rows and all(isinstance(r, list) for r in val)
        if is_grid or (kind == "grid" and has_rows):
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
                    f'{p["pattern"]}.'
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


# ---------------------------------------------------------------- teacher

# The leetcode-teacher skill (.agents/skills/leetcode-teacher) carries ten
# patterns, each with a Python template and a real product it shows up in. This
# corpus is grouped into eighteen NeetCode patterns, so the two vocabularies are
# mapped by hand rather than matched on text — "Linked List" and "Fast & Slow
# Pointers" are the same idea under two names, and nothing textual says so.
# Patterns with no counterpart are simply absent; a wrong template teaches worse
# than none.
TEACHER = ROOT / ".agents" / "skills" / "leetcode-teacher" / "references" / "patterns.md"
PATTERN_MAP = {
    "Two Pointers": "Two Pointers",
    "Sliding Window": "Sliding Window",
    "Linked List": "Fast & Slow Pointers",
    "Intervals": "Merge Intervals",
    "Binary Search": "Binary Search (Modified)",
    "Heap / Priority Queue": "Top K Elements",
    "Graphs": "BFS (Breadth-First Search)",
    "Advanced Graphs": "BFS (Breadth-First Search)",
    "Trees": "DFS (Depth-First Search)",
    "1-D Dynamic Programming": "Dynamic Programming",
    "2-D Dynamic Programming": "Dynamic Programming",
    "Backtracking": "Backtracking",
}


@st.cache_data
def teacher_sections():
    """`## Pattern N: Name` -> the section body, from the skill's reference."""
    try:
        text = TEACHER.read_text()
    except OSError:  # noqa: BLE001 — the skill is optional, the site is not
        return {}
    out, name, buf = {}, None, []
    for line in text.splitlines():
        head = re.match(r"^## Pattern \d+: (.+)$", line)
        if head or line.startswith("## "):
            if name:
                out[name] = "\n".join(buf).strip()
            name, buf = (head.group(1).strip() if head else None), []
        elif name:
            buf.append(line)
    if name:
        out[name] = "\n".join(buf).strip()
    return out


def teaching(pattern):
    """(teacher's name, section markdown) for one of our patterns, or None."""
    named = PATTERN_MAP.get(pattern)
    body = teacher_sections().get(named) if named else None
    return (named, body) if body else None


# ---------------------------------------------------------------- llm

# My keys, a public URL: a stranger must not be able to spend the whole balance by
# holding down enter. A trace costs the most, but Explain is a model call too —
# counting only traces left the cheap path unbounded, which is the one you can
# hold down enter on.
#
# Two counters per path, because they bound different things. The session ones are
# the visible ones and they reset on reload; that is a courtesy limit, not a wall.
# The day ones live in KV (see budget()) and are the wall.
MAX_GEN_PER_SESSION = int(os.environ.get("LEETVIZ_MAX_GENERATIONS", "3"))
MAX_ASK_PER_SESSION = int(os.environ.get("LEETVIZ_MAX_ASKS", "15"))
# Shortest thing worth paying to trace. The real floor is "is this a problem at
# all", which nothing cheap can answer; 8 rejects a stray keystroke while leaving
# room for the shortest genuine names ("wiggle sort" is 11).
MIN_TRACE_CHARS = 8
DAY_CAP = {
    "gen": int(os.environ.get("LEETVIZ_DAY_GENERATIONS", "40")),
    "ask": int(os.environ.get("LEETVIZ_DAY_ASKS", "300")),
}

# Teaching, not lecturing. The order here is the order a good interviewer walks
# you through a problem, and it is why Explain reads differently from a search
# result: pattern first, then the signal that names it, then brute force, then
# why the clever version is cheaper.
_CHAT_SYSTEM = (
    "You are the teacher on LeetViz, a site that plays traced solutions step by "
    "step. Teach pattern-first: name the pattern, say the signal in the problem "
    "that points to it, then the idea in plain words — never a syntax walkthrough. "
    "Say the brute force and what makes it wasteful before the clever version, and "
    "give time and space for both. Where it earns its line, anchor the pattern to "
    "a real product use — top-K to a trending list, intervals to a calendar, trie "
    "to autocomplete — one clause, no story. If the reader sounds stuck rather "
    "than done, give the next hint instead of the finished solution; give the "
    "whole thing when they ask for it. Answer in at most 180 words, plainly. "
    "Never reproduce a LeetCode or NeetCode problem statement verbatim — restate "
    "it in your own words. If you do not know, say so. "
    # Asked about "leetcode 2135" with nothing to go on, the model explained a
    # different problem entirely, in the confident register it uses for the ones
    # it does know. Which title a number maps to is a lookup, and the only
    # trustworthy copy of it is the index below.
    "You cannot reliably recall which problem a LeetCode number refers to. Never "
    "state what a number is unless the site's index has told you in this same "
    "message; if it has not, say you cannot confirm which problem that number is "
    "and ask for the title instead. Guessing it wrong is worse than not knowing."
)


@st.cache_resource
def generator():
    """The one generation layer, imported from api/. There is exactly one prompt,
    one schema and one repair ladder in this repo; a second copy here would drift
    from the deployed one and produce traces this player cannot replay.

    Secrets are copied into os.environ first because api/_gen.py reads all of its
    configuration from the environment by design — Provider builds its URL at
    import time, so this has to happen before the import.
    """
    try:
        for key, value in st.secrets.items():
            if isinstance(value, str) and key not in os.environ:
                os.environ[key] = value
    except Exception:  # noqa: BLE001 — no secrets.toml locally is not an error
        pass
    sys.path.insert(0, str(ROOT / "api"))
    import _gen

    return _gen


def providers():
    """Ready provider ids, or [] when no key/model pair is configured."""
    try:
        return [p.id for p in generator().chain("GENERATE")]
    except Exception as e:  # noqa: BLE001 — a bad import must not blank the page
        st.session_state.llm_error = f"{type(e).__name__}: {e}"
        return []


def retired():
    """Providers this process has given up on, and why.

    Empty unless a key was refused or a balance ran out. It is what tells "no
    model is configured" apart from "the model is configured and its key was
    rejected" — the chain is empty either way, and only one of them is fixed by
    reading the setup block.
    """
    try:
        return dict(generator()._DEAD)
    except Exception:  # noqa: BLE001 — a bad import must not blank the page
        return {}


def failure_advice(e):
    """The one sentence worth reading under a failed generation.

    "A stronger `*_MODEL_GENERATE` is the usual fix" is true of a trace that
    would not replay and false of everything else, but it was printed for every
    failure — so a rejected API key sent the reader off to change the one
    setting that was never the problem. The status code already knows which
    kind of failure this was; this just says so.
    """
    code = getattr(e, "code", None)
    if code in (401, 403):
        return (
            f"**{code} is a credential problem, not a model one.** The provider "
            "rejected the key rather than the request, so a different "
            "`*_MODEL_GENERATE` will not help. Check the key is still live, that "
            "it is pasted whole, and that your account is entitled to the model "
            "it names — on NVIDIA NIM a 403 usually means the key is fine but "
            "has no access to that particular model. Every configured provider "
            "was tried before you saw this."
        )
    if code == 429:
        return ("**Rate-limited upstream**, on every provider configured. Nothing "
                "to fix — a minute is usually enough.")
    if isinstance(code, int) and 500 <= code < 600:
        return (f"**{code} is the provider's outage**, not this app's bug and not "
                "your key. Worth trying again later.")
    return ("A trace that will not replay is refused rather than shown. "
            "A stronger `*_MODEL_GENERATE` is the usual fix.")


def budget(kind):
    """Claim one model call of `kind` against today's budget. False when it is out.

    The session counters beside this one are honest about what they are: session
    state dies on reload and the app says so, which bounds a polite reader and
    nothing else. This counter is keyed by day in the same store the deployed
    API's quota uses — `_lib` already owns the KV client and the day key, so this
    is a second caller, not a second store — and it survives the reload.

    ponytail: check-then-increment, so two simultaneous readers can both take the
    last slot. Atomic INCR-then-compare with a refund is the upgrade path; at
    these caps the worst case is a couple of extra calls, not a bill.

    ponytail: with no KV credentials the store is a file in the container's /tmp,
    so on Streamlit Cloud a container restart resets the day. That is a ceiling,
    not a hole — it bounds a visitor holding down enter, which is the thing it is
    for. Put KV_REST_API_URL/KV_REST_API_TOKEN in the app's secrets to make it
    survive restarts and share one budget with the deployed API.
    """
    lib = generator()._lib
    key = f"st:{kind}:{lib.day_key()}"
    if lib.num(lib.store.get(key)) >= DAY_CAP[kind]:
        return False
    lib.store.incr(key, 1, lib.DAY_TTL)
    return True


def answer(question, history, ground=""):
    """A plain chat answer.

    Reuses _gen's transport, chain order and retry rules rather than reimplementing
    them: the first attempt at this failed on an OpenAI balance that has been
    exhausted for days, because it picked a provider instead of walking the chain.
    Failover fires on the same conditions generation uses, and a provider whose
    account is empty gets marked dead for the process the same way.

    `ground` is what resolve() already worked out from the corpus — the title,
    difficulty and pattern of the problem being asked about. It is passed in
    because the model's recollection of which pattern a problem belongs to is a
    guess and the index is a fact, and the two disagreeing in one reply is worse
    than either alone.
    """
    gen = generator()
    provs = gen.chain("CHEAP") or gen.chain("GENERATE")
    if not provs:
        # The setup block moved into an expander above this reply, so "below" was
        # pointing at the chat box. Every locator in a reply has to agree with
        # where it actually lands.
        return None, ("No model configured, so I cannot answer in words — but naming "
                      "any of the 150 still plays it. See **Running this yourself?** "
                      "above to turn this on.")
    system = _CHAT_SYSTEM
    if ground:
        system += (
            "\n\nThis site's own index says: " + ground + " Those facts win over "
            "your recollection when the two disagree."
        )
    msgs = [{"role": "system", "content": system}]
    for q, a in history[-4:][::-1]:
        msgs += [{"role": "user", "content": q}, {"role": "assistant", "content": a}]
    msgs.append({"role": "user", "content": question})

    for i, prov in enumerate(provs):
        try:
            raw = gen._post(
                {
                    "model": prov.model("CHEAP") or prov.model("GENERATE"),
                    "messages": msgs,
                    "max_completion_tokens": 700,
                },
                prov.key,
                prov.url,
                timeout=90,
            )
            text = ((raw.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
            return prov.id, text.strip() or "(empty answer)"
        except Exception as e:  # noqa: BLE001 — re-raised unless a fallback exists
            gen._mark_if_dead(prov, e)
            if not (i + 1 < len(provs) and gen._retryable(e)):
                raise
    raise RuntimeError("no provider answered")


# ---------------------------------------------------------------- player

TICK = 0.75  # seconds per step when playing, matching the React player's 650ms


# The playback position is deliberately NOT the slider's widget key. Ending
# playback needs an app-scoped rerun from inside the fragment, and that discards
# widget state for widgets the interrupted run never drew — so a position kept in
# the slider's key silently reset to zero the moment the run finished. `pos:` is
# an ordinary session value, and the slider is seeded from it each run.
def _pos(skey):
    return f"pos:{skey}"


def _slider(skey):
    return f"sl:{skey}"


def _seek(skey, to, last):
    st.session_state[_pos(skey)] = max(0, min(to, last))
    st.session_state.playing = False


def _nudge(skey, delta, last):
    _seek(skey, st.session_state.get(_pos(skey), 0) + delta, last)


def _scrub(skey):
    """The user dragged the slider, so that becomes the position and play stops."""
    st.session_state[_pos(skey)] = st.session_state[_slider(skey)]
    st.session_state.playing = False


def _toggle(skey, last):
    # Pressing play on the last step replays from the top, the way a video does.
    if not st.session_state.playing and st.session_state.get(_pos(skey), 0) >= last:
        st.session_state[_pos(skey)] = 0
    st.session_state.playing = not st.session_state.playing


def transport(skey, last):
    """The buttons. Rendered by the caller, deliberately OUTSIDE the fragment.

    A click on a widget inside a fragment reruns only that fragment, so the
    `st.fragment(run_every=…)` wrapper in player() never re-executes and never
    learns that play was pressed: the step advanced exactly once and then sat
    there. Out here a click is an ordinary app rerun, which re-reads run_every
    and arms or drops the timer.
    """
    bar = st.columns([1, 1, 1, 1, 1, 14])
    playing = st.session_state.playing
    for n, (col, label, help_, cb, args) in enumerate((
        (bar[0], "⏮", "First step", _seek, (skey, 0, last)),
        (bar[1], "◀", "Previous step", _nudge, (skey, -1, last)),
        (bar[2], "⏸" if playing else "▶", "Pause" if playing else "Play", _toggle, (skey, last)),
        (bar[3], "⏵", "Next step", _nudge, (skey, 1, last)),
        (bar[4], "⏭", "Last step", _seek, (skey, last, last)),
    )):
        # The key is index-based, not label-based: a key with a space in it
        # becomes two CSS classes, and the play button's label changes on every
        # toggle, which would churn the widget's identity.
        col.button(label, help=help_, on_click=cb, args=args, key=f"tp_{n}:{skey}")


def stage(approach, variant, skey):
    """Code, state, narration, scrubber. Re-runs on its own while playing."""
    steps = variant["steps"]
    last = len(steps) - 1

    i = min(st.session_state.get(_pos(skey), 0), last)
    if st.session_state.playing:
        if i >= last:
            # Drop the timer. Only the caller reads run_every, so this has to
            # leave the fragment; the position survives because it is not a
            # widget key.
            st.session_state.playing = False
            st.rerun(scope="app")
        i += 1
        st.session_state[_pos(skey)] = i
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

    bar = st.columns([16, 3])
    # Seeded before the widget exists, which is the only moment Streamlit allows
    # writing a widget's key. The slider is a view of the position, never its home.
    st.session_state[_slider(skey)] = i
    bar[0].slider(
        "Step", 0, last, key=_slider(skey), on_change=_scrub, args=(skey,),
        label_visibility="collapsed",
    )
    bar[1].markdown(f'<div class="lv-count">{i + 1} / {last + 1}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- page


def _close():
    st.session_state.open = False
    st.session_state.playing = False


# `view` is deliberately NOT the radio's key. Asking for a problem that is
# already traced has to switch the view from inside the Ask page — after the
# radio has been instantiated — and Streamlit refuses to let a widget's key be
# written once its widget exists. So `view` is an ordinary session value and the
# radio is a view of it, seeded each run and copied back on change. Same
# arrangement as the player's position and its slider, for the same reason.
def _nav():
    st.session_state.view = st.session_state.nav


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


def player(problem, scope):
    """Header-free renderer for one problem: approach, variant, autoplaying stage."""
    approach = pick("approach", problem["approaches"], scope)
    st.markdown(
        f'<div class="lv-cx">time {approach["complexity"]["time"]} · '
        f'space {approach["complexity"]["space"]}</div>',
        unsafe_allow_html=True,
    )
    variant = pick("variant", approach["variants"], f'{scope}:{approach["id"]}')
    skey = f'{scope}:{approach["id"]}:{variant["id"]}'
    transport(skey, len(variant["steps"]) - 1)
    # run_every is read when the decorator is applied, so applying it per run is
    # what lets play and pause actually start and stop the timer.
    st.fragment(run_every=TICK if st.session_state.playing else None)(stage)(
        approach, variant, skey
    )


SETUP = """
Add these to **Manage app → Settings → Secrets**, then rerun. Any one provider
is enough; the chain tries them in order and fails over.

```toml
GEMINI_API_KEY = "AIza…"
GEMINI_MODEL_GENERATE = "gemini-2.5-flash"
GEMINI_MODEL_CHEAP = "gemini-2.5-flash"

# optional extras, same shape
# OPENAI_API_KEY = "sk-…"
# OPENAI_MODEL_GENERATE = "gpt-5"
# NVIDIA_API_KEY = "nvapi-…"
# NVIDIA_MODEL_GENERATE = "openai/gpt-oss-20b"
SOLVE_PROVIDER_ORDER = "google,openai,nvidia"
```
"""


def ask_view(problems):
    """The chatbot. Two send modes, because one of them costs real money."""
    st.markdown('<div class="lv-title">Ask</div>', unsafe_allow_html=True)
    live = providers()
    if live:
        st.markdown(
            pill(" · ".join(live))
            + pill(f"{MAX_GEN_PER_SESSION - st.session_state.made} traces left this session")
            + pill(f"{MAX_ASK_PER_SESSION - st.session_state.asks} questions left"),
            unsafe_allow_html=True,
        )
    else:
        # What a visitor needs to know is one sentence: naming any of the 150
        # still works. The secrets block underneath is for whoever runs the app,
        # and it was being shown to everyone who opened the page — a config dump
        # is not an answer to "what is this". It stays, one click down.
        #
        # "No model is configured" is only one of the two ways to end up here, and
        # after a refused key it is the wrong one: retiring the provider empties
        # the chain, so a configured-but-rejected key started reporting itself as
        # a missing one and sent the reader to the setup block to fix a setting
        # that was already correct.
        gone = retired()
        if gone:
            st.caption(
                "Free-form answers are off — every configured provider refused this "
                f"app's key ({', '.join(f'{k}: {v}' for k, v in gone.items())}). That is "
                "a credential problem, not a missing setting. Naming any of the 150 "
                "still plays it, and that path needs no key at all."
            )
        else:
            st.caption(
                "Free-form answers are off right now — no model is configured. Naming any "
                "of the 150 still plays it, and that path needs no key at all."
            )
        with st.expander("Running this yourself? Turn Ask on"):
            st.markdown(SETUP)
            if st.session_state.get("llm_error"):
                st.caption(f"Import failed: {st.session_state.llm_error}")

    mode = st.segmented_control(
        "mode", ["Explain", "Trace it"], default="Explain", key="askmode",
        label_visibility="collapsed",
    )
    st.caption(
        "Name any of the 150 — “leetcode 25”, “two sum”, “sliding window” — and it "
        "plays right here. **Explain** teaches it — pattern first, brute force, then "
        "why the fast version is faster; **Trace it** generates "
        "a new visualization, in the same shape as the 150, for anything outside them."
    )

    asked = st.chat_input("Ask anything, or paste a problem statement to trace")
    if asked:
        # A problem already in the corpus is answered from disk. Paying a model
        # to redo work that is sitting in traces/ would be the expensive way to
        # get a worse answer.
        slug, reply = resolve(asked, problems)
        # Whatever the question was, if it named one of the 150 that trace is
        # what the answer looks like. Showing it here rather than pointing at
        # another page is the whole point of the Ask view.
        st.session_state.shown = slug
        if slug:
            watch(slug)
        if slug and mode == "Trace it":
            st.session_state.traced = None  # the committed trace wins over a stale one
            st.session_state.chat = [(asked, reply + " Already traced — playing above.")] + \
                st.session_state.chat[:9]
            st.rerun()
        elif mode == "Trace it":
            if not live:
                st.session_state.chat = [(asked, "No model configured — see the setup above.")] + \
                    st.session_state.chat[:9]
            elif st.session_state.made >= MAX_GEN_PER_SESSION:
                st.session_state.chat = [
                    (asked, f"Session limit of {MAX_GEN_PER_SESSION} generations reached. "
                            "Reload to start a new session.")
                ] + st.session_state.chat[:9]
            # A generation is 30-60s and real money, and "t" is not a problem.
            # The gates below count what was spent; this one is about not
            # spending it on a typo in the first place. Deliberately generous —
            # "wiggle sort" is a real problem name and has to get through.
            elif len(asked.strip()) < MIN_TRACE_CHARS:
                st.session_state.chat = [
                    (asked, f"That is too short to trace — give me a problem name or "
                            f"its statement, at least {MIN_TRACE_CHARS} characters. "
                            "**Explain** answers short questions; **Trace it** has to "
                            "build a whole visualization, so it needs something to build "
                            "from.")
                ] + st.session_state.chat[:9]
            elif not budget("gen"):
                st.session_state.chat = [
                    (asked, f"This site has generated its {DAY_CAP['gen']} traces for today — "
                            "the budget resets tomorrow. All 150 committed traces still play, "
                            "and **Explain** still answers.")
                ] + st.session_state.chat[:9]
            else:
                with st.spinner("Tracing — this runs the real generator, ~30-60s"):
                    try:
                        problem, cost, _usage = generator().generate(asked)
                        st.session_state.made += 1
                        st.session_state.traced = problem
                        st.session_state.shown = None  # the new trace is the answer
                        st.session_state.chat = [
                            (asked, f'Traced **{problem["title"]}** — '
                                    f'{len(problem["approaches"])} approaches. Below.')
                        ] + st.session_state.chat[:9]
                    except Exception as e:  # noqa: BLE001 — the reason must not leak a key
                        # The validator's reason is the useful part ("the ops and
                        # the result disagree" tells you the model, not the app,
                        # was wrong). It is our own text, but it goes through the
                        # redactor anyway — upstream prose can quote a key.
                        why = generator()._lib.redact(str(e))[:400]
                        st.session_state.chat = [
                            (asked, f"**Generation failed.** {type(e).__name__}: {why}\n\n"
                                    + failure_advice(e))
                        ] + st.session_state.chat[:9]
        elif live and st.session_state.asks >= MAX_ASK_PER_SESSION:
            st.session_state.chat = [
                (asked, f"Session limit of {MAX_ASK_PER_SESSION} questions reached. "
                        "Reload to start a new session — the 150 traces need no model.")
            ] + st.session_state.chat[:9]
        elif live and not budget("ask"):
            st.session_state.chat = [
                (asked, "This site has answered its questions for today — the budget resets "
                        "tomorrow. Every one of the 150 traces still plays.")
            ] + st.session_state.chat[:9]
        else:
            with st.spinner("Thinking"):
                try:
                    # resolve() bolds a title or a pattern exactly when it found
                    # one; its other replies ("No match. Try a…") are instructions
                    # to the reader, not facts about the corpus, and grounding on
                    # those would have the teacher explain the search box.
                    # Everything resolve() worked out is a fact about the corpus
                    # and belongs in the prompt; only its two "try a number, a
                    # title or a pattern" nudges are instructions to the reader.
                    # Dropping the rest threw away the most useful fact there is
                    # — "LeetCode 2135 is not one of the 150" — and left the
                    # model to recall the numbering itself, which it cannot do:
                    # asked for 2135 it confidently explained a different
                    # problem. The index knows; the model guesses.
                    facts = "" if reply.startswith(("Ask for a problem", "No match.")) else reply
                    if slug:
                        # Only a slug puts a player on screen. Saying so for a
                        # pattern listing would be a locator pointing at nothing.
                        facts += " That trace is playing above your reply, so teach it."
                        # The reader can expand this same template under the
                        # trace. An answer that taught a different shape than
                        # the one on screen would be teaching against itself.
                        lesson = teaching(
                            next(p for p in problems if p["slug"] == slug)["pattern"]
                        )
                        if lesson:
                            facts += (
                                f"\n\nThe house template for this pattern ({lesson[0]}), "
                                f"which the reader can open under the trace — stay "
                                f"consistent with it:\n{lesson[1]}"
                            )
                    who, text = answer(asked, st.session_state.chat, facts)
                    st.session_state.asks += 1
                    if slug:
                        # The panel renders above this answer, so say so — every
                        # locator in a reply has to agree with where it lands.
                        text += f"\n\n*{reply} Playing above.*"
                    st.session_state.chat = [(asked, text)] + st.session_state.chat[:9]
                except Exception as e:  # noqa: BLE001
                    st.session_state.chat = [
                        (asked, f"That call failed: {type(e).__name__}.")
                    ] + st.session_state.chat[:9]
        st.rerun()

    # Both branches render through problem_panel, the same function the Problems
    # page uses. A committed trace and a generated one differ by their pills and
    # by nothing else.
    shown = st.session_state.get("shown")
    made = st.session_state.get("traced")
    if shown:
        st.divider()
        entry = next(p for p in problems if p["slug"] == shown)
        problem_panel(load_trace(shown), f"ask:{shown}", lc=entry["lc"])
    elif made:
        st.divider()
        problem_panel(made, "generated", tag="generated, not committed")

    for q, a in st.session_state.chat:
        st.markdown(f'<div class="lv-ask">{html.escape(q)}</div>', unsafe_allow_html=True)
        st.markdown(a)


def open_problem(slug):
    """Row click: show that problem and count it as watched."""
    st.session_state.slug = slug
    st.session_state.open = True
    st.session_state.playing = False
    watch(slug)


def roadmap_view(index, problems):
    """The problem list, NeetCode's shape: one section per pattern, each row a
    number, a title, a difficulty and a tick once you have watched it.

    Progress is real rather than decorative — it counts what this session has
    actually opened. Nothing is persisted, so nothing is claimed that a reload
    would contradict.
    """
    seen = st.session_state.seen
    st.markdown('<div class="lv-title">The 150, traced line by line</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<p class="lv-prompt">Every problem below runs for real. Python traced it '
        'ahead of time; press play and watch the variables move.</p>',
        unsafe_allow_html=True,
    )

    bar = st.columns([3, 2], vertical_alignment="center")
    q = bar[0].text_input(
        "Search", placeholder="Search by name, number or pattern", label_visibility="collapsed"
    ).strip().lower()
    level = bar[1].segmented_control(
        "Difficulty", ["Easy", "Medium", "Hard"], key="level", label_visibility="collapsed"
    )
    pool = [
        p for p in problems
        if (not q or q in p["title"].lower() or q in p["pattern"].lower()
            or q in str(p["leetcode"]))
        and (not level or p["difficulty"] == level)
    ]
    if not pool:
        st.caption("Nothing matches that. The corpus is the NeetCode 150.")
        return

    done = len([p for p in pool if p["slug"] in seen])
    st.markdown(
        f'{pill(f"{len(pool)} problems")}{pill(f"{done} watched")}', unsafe_allow_html=True
    )

    for pattern in index["patterns"]:
        rows = [p for p in pool if p["pattern"] == pattern]
        if not rows:
            continue
        hit = len([p for p in rows if p["slug"] in seen])
        st.markdown(
            f'<div class="lv-sec"><b>{html.escape(pattern)}</b>'
            f'<div class="lv-bar"><i style="width:{hit * 100 // len(rows)}%"></i></div>'
            f"<span>{hit} / {len(rows)}</span></div>"
            '<div class="lv-head">&nbsp;</div>',
            unsafe_allow_html=True,
        )
        for p in rows:
            cols = st.columns([1, 12, 2, 1], gap="small", vertical_alignment="center")
            cols[0].markdown(f'<div class="lv-num">{p["leetcode"]}</div>',
                             unsafe_allow_html=True)
            cols[1].button(
                p["title"], key=f'go_{p["slug"]}', on_click=open_problem, args=(p["slug"],),
                use_container_width=True, disabled=not p["ready"],
            )
            cols[2].markdown(
                f'<div class="lv-rowcell">{pill(p["difficulty"], p["difficulty"])}</div>',
                unsafe_allow_html=True,
            )
            cols[3].markdown(
                f'<div class="lv-seen">{"✓" if p["slug"] in seen else ""}</div>',
                unsafe_allow_html=True,
            )


def problem_panel(trace, scope, lc=None, tag=None):
    """Title, tags, prompt, examples, player — the one renderer for a problem.

    Every caller goes through here, so a problem looks the same whether you
    reached it from the roadmap, by asking for it by name, or by generating it.
    Two copies of this would drift, and a trace shown in the Ask view looking
    unlike the 150 is exactly the bug this replaced.
    """
    st.markdown(f'<div class="lv-title">{html.escape(trace["title"])}</div>',
                unsafe_allow_html=True)
    tags = pill(trace.get("difficulty") or "", trace.get("difficulty") or "")
    tags += pill(trace.get("pattern") or "generated")
    if lc:
        tags += (
            f'<a class="lv-pill link" target="_blank" rel="noopener noreferrer" '
            f'href="https://leetcode.com/problems/{lc}/">LeetCode '
            f'{trace.get("leetcode", "")} ↗</a>'
            f'<a class="lv-pill link" target="_blank" rel="noopener noreferrer" '
            f'href="https://neetcode.io/problems/{lc}">NeetCode ↗</a>'
        )
    if tag:
        tags += pill(tag)
    st.markdown(tags, unsafe_allow_html=True)

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

    player(trace, scope)
    st.caption("Press ▶ to watch it run. Every step is the real traced state, not an animation.")

    # The trace shows this one problem solved. The pattern is what carries over
    # to the next one, so the skill's template sits right under it — collapsed,
    # because it is the second thing you want, not the first.
    lesson = teaching(trace.get("pattern") or "")
    if lesson:
        named, body = lesson
        with st.expander(f"The pattern: {named}"):
            st.markdown(body)


def problem_view(problems, ready):
    choice = next(p for p in problems if p["slug"] == st.session_state.slug)

    # Prev/next walk the roadmap order, so paging through is paging through the
    # pattern the way NeetCode's own next-problem arrow does.
    at = ready.index(choice)
    nav = st.columns([2, 1, 1, 10], vertical_alignment="center")
    nav[0].button("← All problems", key="nav_back", on_click=_close)
    if at:
        nav[1].button("Prev", key="nav_prev", on_click=open_problem,
                      args=(ready[at - 1]["slug"],))
    if at + 1 < len(ready):
        nav[2].button("Next", key="nav_next", on_click=open_problem,
                      args=(ready[at + 1]["slug"],))

    problem_panel(load_trace(choice["slug"]), choice["slug"], lc=choice["lc"])


def main():
    # expanded, not "auto": the sidebar is the only way to reach Ask, and on
    # Streamlit Cloud auto resolved to collapsed.
    st.set_page_config(page_title="LeetViz", page_icon="◆", layout="wide",
                       initial_sidebar_state="expanded")
    st.markdown(CSS, unsafe_allow_html=True)

    index = load_index()
    problems = index["problems"]
    ready = [p for p in problems if p["ready"]]
    st.session_state.setdefault("slug", ready[0]["slug"])
    st.session_state.setdefault("playing", False)
    st.session_state.setdefault("chat", [])
    st.session_state.setdefault("made", 0)
    st.session_state.setdefault("asks", 0)
    st.session_state.setdefault("view", "Problems")
    st.session_state.setdefault("open", False)
    # Seeded from the URL, so a refresh keeps its ticks. setdefault, not assign:
    # after the first run of a session the session state is the live copy and the
    # query parameter is only its echo.
    st.session_state.setdefault("seen", decode_seen(st.query_params.get("p", ""), all_slugs()))
    st.session_state.setdefault("shown", None)

    with st.sidebar:
        st.markdown('<div class="lv-brand">LeetViz</div>', unsafe_allow_html=True)
        # Seeded before the widget exists, the only moment Streamlit allows a
        # widget's key to be written.
        st.session_state.nav = st.session_state.view
        st.radio("View", ["Problems", "Ask"], key="nav", horizontal=True,
                 on_change=_nav, label_visibility="collapsed")
        if st.session_state.view == "Problems":
            st.caption(f"{len(ready)} problems traced line by line, replayed from JSON")
            watched = len(st.session_state.seen)
            st.progress(watched / len(ready), text=f"{watched} / {len(ready)} watched")
            # Progress rides in the URL, which is no use to anyone who does not
            # know it is there. Only worth saying once there is something to keep.
            if watched:
                st.caption("Bookmark this page to keep your progress — it travels "
                           "with the link, so it opens the same on your phone.")
        else:
            st.caption("Name one of the 150 and it plays here. Ask anything else in "
                       "words, or generate a trace for a problem outside them.")

    if st.session_state.view == "Ask":
        ask_view(problems)
    elif st.session_state.open:
        problem_view(problems, ready)
    else:
        roadmap_view(index, problems)


if __name__ == "__main__":
    main()
