"""LeetViz on Streamlit.

The Next.js app is the primary front end; this is a second reader over the same
committed artifacts. It reads `traces/*.json` directly — no Python tracing here,
no server, no API. Ops are folded forward exactly the way `lib/fold.ts` does it,
so a step shown here is the step the React player shows.
"""

import html
import json
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

CSS = """
<style>
.lv-src { font: 13px/1.55 ui-monospace, SFMono-Regular, Menlo, monospace;
          border:1px solid #e3e3e6; border-radius:8px; overflow-x:auto; }
.lv-src div { padding:1px 12px; white-space:pre; }
.lv-src div.on { background:#fff4d6; box-shadow:inset 3px 0 0 #e0a800; }
.lv-note { border-left:3px solid #e0a800; padding:6px 12px; margin:10px 0;
           background:#fffaf0; font-size:14px; }
.lv-cells { display:flex; flex-wrap:wrap; gap:4px; margin:2px 0 10px; }
.lv-cell { min-width:38px; text-align:center; border:1px solid #d9d9de;
           border-radius:6px; padding:4px 6px; font:13px ui-monospace, monospace; }
.lv-cell.mark { background:#ffe9a8; border-color:#e0a800; }
.lv-idx { font-size:10px; color:#8a8a92; }
.lv-ptr { font-size:11px; color:#b26a00; height:14px; }
.lv-name { font:12px ui-monospace, monospace; color:#5a5a63; margin-top:6px; }
.lv-name b { color:#111; }
.lv-grid { border-collapse:collapse; margin:2px 0 10px; }
.lv-grid td { border:1px solid #d9d9de; padding:4px 9px; text-align:center;
              font:13px ui-monospace, monospace; }
.lv-grid td.mark { background:#ffe9a8; }
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
                    f'stroke="#b9b9c0" stroke-width="1.5" />'
                )
        tags = labels.get(nid, [])
        fill = "#ffe9a8" if tags else "#fff"
        circles.append(
            f'<circle cx="{x0}" cy="{y0}" r="{r}" fill="{fill}" stroke="#8a8a92" />'
            f'<text x="{x0}" y="{y0 + 4}" text-anchor="middle">'
            f'{html.escape(str(node.get("val")))}</text>'
        )
        if tags:
            circles.append(
                f'<text x="{x0}" y="{y0 - r - 6}" text-anchor="middle" fill="#b26a00">'
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
                f'stroke="#b9b9c0" stroke-width="1.5" />'
            )
        done = c.get("status") != "active"
        args = ", ".join(f"{k}={v}" for k, v in (c.get("args") or {}).items())
        text = f'{c.get("fn")}({args})'
        if done and c.get("ret") is not None:
            text += f' → {c["ret"]}'
        parts.append(
            f'<rect x="{x0}" y="{y0 - 12}" width="{sx - 14}" height="24" rx="6" '
            f'fill="{"#f2f2f4" if done else "#ffe9a8"}" stroke="#c9c9d0" />'
            f'<text x="{x0 + 8}" y="{y0 + 4}">{html.escape(text[:22])}</text>'
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
                    f'stroke="#b9b9c0" stroke-width="1.5" />'
                )
    for k in keys:
        a = px.get(str(k))
        if not a:
            continue
        hot = str(k) in marked
        circles.append(
            f'<circle cx="{a[0]}" cy="{a[1]}" r="19" '
            f'fill="{"#ffe9a8" if hot else "#fff"}" stroke="#8a8a92" />'
            f'<text x="{a[0]}" y="{a[1] + 4}" text-anchor="middle">{html.escape(str(k))}</text>'
        )
        tag = labels.get(str(k))
        if tag is not None:
            circles.append(
                f'<text x="{a[0]}" y="{a[1] - 25}" text-anchor="middle" fill="#b26a00">'
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


# ---------------------------------------------------------------- page

def main():

    st.set_page_config(page_title="LeetViz", page_icon="◆", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)

    index = load_index()
    ready = [p for p in index["problems"] if p["ready"]]

    with st.sidebar:
        st.markdown("### LeetViz")
        st.caption(f"{len(ready)} traced problems · replayed from committed JSON")
        patterns = ["All"] + [p for p in index["patterns"] if any(q["pattern"] == p for q in ready)]
        pattern = st.selectbox("Pattern", patterns)
        pool = [p for p in ready if pattern == "All" or p["pattern"] == pattern]
        choice = st.selectbox(
            "Problem",
            pool,
            format_func=lambda p: f'{p["leetcode"]}. {p["title"]}  ({p["difficulty"]})',
        )

    trace = load_trace(choice["slug"])
    st.title(trace["title"])
    meta = f'{trace.get("difficulty", "")} · {trace["pattern"]}'
    if trace.get("leetcode"):
        meta += f' · [LeetCode {trace["leetcode"]}](https://leetcode.com/problems/{choice["lc"]}/)'
    st.markdown(meta)

    if trace.get("prompt"):
        st.write(trace["prompt"])
    with st.expander("Examples and constraints"):
        for ex in trace.get("examples", []):
            st.markdown(f'**In** `{ex["input"]}` → **Out** `{ex["output"]}`')
            if ex.get("why"):
                st.caption(ex["why"])
        for c in trace.get("constraints", []):
            st.markdown(f"- {c}")

    tabs = st.tabs([a["label"] for a in trace["approaches"]])
    for tab, approach in zip(tabs, trace["approaches"]):
        with tab:
            st.caption(
                f'Time {approach["complexity"]["time"]} · Space {approach["complexity"]["space"]}'
            )
            variant = st.radio(
                "Variant",
                approach["variants"],
                format_func=lambda v: v["label"],
                horizontal=True,
                key=f'{choice["slug"]}-{approach["id"]}-variant',
            )
            steps = variant["steps"]
            i = st.slider(
                "Step",
                0,
                len(steps) - 1,
                0,
                key=f'{choice["slug"]}-{approach["id"]}-{variant["id"]}-step',
            )
            step = steps[i]
            left, right = st.columns([1, 1])
            with left:
                st.markdown(source_html(approach["source"], step["line"]), unsafe_allow_html=True)
                if step.get("note"):
                    st.markdown(
                        f'<div class="lv-note">{html.escape(step["note"])}</div>',
                        unsafe_allow_html=True,
                    )
            with right:
                st.markdown(
                    render_state(
                        state_at(steps, i), approach["viz"], approach["layout"], touched(step)
                    ),
                    unsafe_allow_html=True,
                )
                if i == len(steps) - 1:
                    st.success(f'returns {json.dumps(variant["result"])}')


if __name__ == "__main__":
    main()
