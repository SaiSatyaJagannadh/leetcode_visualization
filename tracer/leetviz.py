"""Line-by-line tracer. Runs a solution under sys.settrace and emits diff ops.

Narration comes from `#>` comments in the source, so authors write one file.
A `#>` on a code line annotates that line; a `#>` on its own annotates the next.

Two reserved state keys carry things plain locals can't express:
  $nodes  the object graph (ListNode/TreeNode) reachable from locals, with
          frozen coordinates, referenced from locals as {"$ref": nid}
  $calls  the recursion call tree, when the traced function calls itself
Both are ordinary dicts, so the generic differ produces ops for them unchanged.
"""

import inspect
import json
import math
import sys

from structs import NODE_TYPES, ListNode, TreeNode

SCHEMA_VERSION = 1
MAX_STEPS = 4000
ATOMS = (int, float, str, bool, type(None))

_SKIP = object()
_MISSING = object()


class Snapshotter:
    """Serialises locals, capturing the reachable node graph as it goes."""

    def __init__(self):
        self.coords = {}  # nid -> [x, y], assigned once and never moved
        self.nodes = {}
        self._free = 0.0

    def snapshot(self, loc):
        self.nodes = {}
        snap = {}
        for k, v in loc.items():
            if k.startswith("_"):
                continue
            s = self.safe(v)
            if s is not _SKIP:
                snap[k] = s
        if self.nodes:
            snap["$nodes"] = self.nodes
        return snap

    def safe(self, v, depth=0):
        if isinstance(v, NODE_TYPES):
            return self.node(v)
        if isinstance(v, float) and not math.isfinite(v):
            return "NaN" if math.isnan(v) else ("∞" if v > 0 else "-∞")
        if isinstance(v, ATOMS):
            return v
        if depth > 4:
            return _SKIP
        if isinstance(v, (list, tuple, set, frozenset)):
            items = sorted(v, key=repr) if isinstance(v, (set, frozenset)) else v
            out = []
            for x in items:
                s = self.safe(x, depth + 1)
                if s is _SKIP:
                    return _SKIP
                out.append(s)
            return out
        if isinstance(v, dict):
            out = {}
            for k, x in v.items():
                if not isinstance(k, ATOMS):
                    return _SKIP
                s = self.safe(x, depth + 1)
                if s is _SKIP:
                    return _SKIP
                out[str(k)] = s
            return out
        return _SKIP

    def node(self, n):
        nid = str(n.nid)
        if nid in self.nodes:
            return {"$ref": nid}
        self.nodes[nid] = None  # reserve first: lists and trees may cycle
        if isinstance(n, ListNode):
            d = {"kind": "list", "val": self.safe(n.val), "next": self.link(n.next)}
        else:
            d = {
                "kind": "tree",
                "val": self.safe(n.val),
                "left": self.link(n.left),
                "right": self.link(n.right),
            }
        d["at"] = self.place(n, nid)
        self.nodes[nid] = d
        return {"$ref": nid}

    def link(self, n):
        return self.node(n) if n is not None else None

    def place(self, n, nid):
        if nid in self.coords:
            return self.coords[nid]
        if n.pos is not None:
            xy = [n.pos[0], n.pos[1]]
        else:
            # Built during the run (merge, insert). Park it clear of the rest.
            self._free = max(self._free, max((c[0] for c in self.coords.values()), default=-1) + 1)
            xy = [self._free, 0.0]
            self._free += 1
        self.coords[nid] = xy
        return xy


def _diff(path, old, new, out):
    """Append ["set", path, value] / ["del", path] ops turning old into new."""
    if type(old) is type(new) and old == new:
        return
    if isinstance(old, list) and isinstance(new, list) and len(old) == len(new):
        for i, (a, b) in enumerate(zip(old, new)):
            _diff(path + [i], a, b, out)
        return
    if isinstance(old, dict) and isinstance(new, dict):
        for k in old:
            if k not in new:
                out.append(["del", path + [k]])
        for k, v in new.items():
            _diff(path + [k], old.get(k, _MISSING), v, out)
        return
    out.append(["set", path, new])


def _notes(src, first):
    """{absolute lineno: narration} from `#>` markers."""
    notes = {}
    pending = None
    for off, line in enumerate(src):
        stripped = line.strip()
        text = stripped.split("#>", 1)[1].strip() if "#>" in stripped else None
        if stripped.startswith("#>"):
            pending = text
        elif text is not None:
            notes[first + off] = text
        elif pending and stripped and not stripped.startswith("#"):
            notes[first + off] = pending
            pending = None
    return notes


def trace(fn, args):
    """Run fn(**args) traced. Returns (steps, result, source_lines)."""
    src, first = inspect.getsourcelines(fn)
    notes = _notes(src, first)
    code = fn.__code__
    snap = Snapshotter()
    steps = []
    prev = {}
    pending = first  # the line whose effects we haven't emitted yet

    # Recursion: same code object, so recursive frames are already traced. All
    # that's missing is who called whom.
    calls = {}
    stack = []
    counter = [0]

    def emit(lineno, ops):
        steps.append({"line": lineno - first, "note": notes.get(lineno), "ops": ops})

    def record(lineno, loc):
        # A line event fires *before* the line runs, so the state we see is the
        # result of the previous line. Attribute it there.
        nonlocal prev, pending
        if len(steps) >= MAX_STEPS:
            return
        state = snap.snapshot(loc)
        if len(calls) > 1:  # one call is not recursion
            state["$calls"] = json.loads(json.dumps(calls))
        ops = []
        _diff([], prev, state, ops)
        emit(pending, ops)
        prev = state
        pending = lineno

    def enter(frame):
        cid = str(counter[0])
        counter[0] += 1
        # Node args show their value, not a $ref — a call tree reads better as
        # solve(node=3) than solve(node={"$ref":"7"}).
        args_in = {}
        for k in code.co_varnames[: code.co_argcount]:
            raw = frame.f_locals.get(k)
            v = snap.safe(raw.val if isinstance(raw, NODE_TYPES) else raw)
            if v is not _SKIP:
                args_in[k] = v
        calls[cid] = {
            "parent": stack[-1] if stack else None,
            "depth": len(stack),
            "args": args_in,
            "ret": None,
            "status": "active",
            "enteredAt": len(steps),
            "at": [float(counter[0] - 1), float(len(stack))],
        }
        stack.append(cid)
        return cid

    def local_trace(frame, event, arg):
        if event == "line":
            record(frame.f_lineno, frame.f_locals)
        elif event == "return":
            record(frame.f_lineno, frame.f_locals)
            if stack:
                cid = stack.pop()
                calls[cid]["status"] = "returned"
                calls[cid]["ret"] = None if (r := snap.safe(arg)) is _SKIP else r
        return local_trace

    def global_trace(frame, event, arg):
        if event == "call" and frame.f_code is code:
            enter(frame)
            return local_trace
        return None

    sys.settrace(global_trace)
    try:
        result = fn(**args)
    finally:
        sys.settrace(None)

    # The outermost frame is popped after its last line event, so its return has
    # to be flushed here or the root stays "active" forever.
    tail = []
    if len(calls) > 1:
        final = dict(prev)
        final["$calls"] = json.loads(json.dumps(calls))
        _diff([], prev, final, tail)
    if steps and steps[-1]["line"] != pending - first:
        emit(pending, tail)  # land on the returning line
    elif tail:
        steps[-1]["ops"].extend(tail)
    if len(steps) >= MAX_STEPS:
        raise RuntimeError(f"{fn.__name__} exceeded {MAX_STEPS} steps")

    # Narration renders separately: drop the `#>` lines and renumber the steps.
    keep = [i for i, l in enumerate(src) if not l.strip().startswith("#>")]
    remap = {old: new for new, old in enumerate(keep)}
    for s in steps:
        s["line"] = remap[s["line"]]
    return steps, snap.safe(result), [src[i].split("#>")[0].rstrip() for i in keep]


def circle_layout(keys):
    """Coordinates for graph vars, which are plain adjacency dicts, not objects."""
    n = max(len(keys), 1)
    return {
        str(k): [
            round(math.cos(2 * math.pi * i / n - math.pi / 2), 4),
            round(math.sin(2 * math.pi * i / n - math.pi / 2), 4),
        ]
        for i, k in enumerate(keys)
    }


def build_problem(mod):
    """Turn a solution module (META / VARIANTS / APPROACHES) into a trace file."""
    approaches = []
    for a in mod.APPROACHES:
        variants = []
        for v in mod.VARIANTS:
            # A factory, when the input holds nodes the algorithm will mutate.
            inp = v["input"]
            steps, result, src = trace(a["fn"], inp() if callable(inp) else dict(inp))
            variants.append(
                {
                    "id": v["id"],
                    "label": v["label"],
                    "note": v.get("note"),
                    "result": result,
                    "steps": steps,
                }
            )
        # Graphs are adjacency dicts, so their layout is static per approach.
        layout = {}
        for name, spec in a.get("viz", {}).items():
            if spec == "graph":
                keys = _graph_keys(variants, name)
                if keys:
                    layout[name] = circle_layout(keys)
        approaches.append(
            {
                "id": a["id"],
                "label": a["label"],
                "complexity": a["complexity"],
                "viz": a.get("viz", {}),
                "layout": layout,
                "source": src,
                "variants": variants,
            }
        )
    return {"schemaVersion": SCHEMA_VERSION, **mod.META, "approaches": approaches}


def _graph_keys(variants, name):
    """Every node id the graph var ever holds, across all variants."""
    keys = []
    for v in variants:
        for s in v["steps"]:
            for op in s["ops"]:
                if op[0] == "set" and op[1] and op[1][0] == name and len(op[1]) == 1:
                    for k in op[2] if isinstance(op[2], dict) else []:
                        if k not in keys:
                            keys.append(k)
    return keys


def dump(obj, path):
    path.write_text(json.dumps(obj, separators=(",", ":")))
