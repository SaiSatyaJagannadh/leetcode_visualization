"""Line-by-line tracer. Runs a solution under sys.settrace and emits diff ops.

Narration comes from `#>` comments in the source, so authors write one file.
A `#>` on a code line annotates that line; a `#>` on its own annotates the next.
"""

import inspect
import json
import math
import sys

SCHEMA_VERSION = 1
MAX_STEPS = 2000
ATOMS = (int, float, str, bool, type(None))

_SKIP = object()
_MISSING = object()


def _safe(v, depth=0):
    """JSON-safe copy of v, or _SKIP if it can't be represented."""
    if isinstance(v, float) and not math.isfinite(v):
        return "NaN" if math.isnan(v) else ("∞" if v > 0 else "-∞")
    if isinstance(v, ATOMS):
        return v
    if depth > 3:
        return _SKIP
    if isinstance(v, (list, tuple, set, frozenset)):
        items = sorted(v, key=repr) if isinstance(v, (set, frozenset)) else v
        out = []
        for x in items:
            s = _safe(x, depth + 1)
            if s is _SKIP:
                return _SKIP
            out.append(s)
        return out
    if isinstance(v, dict):
        out = {}
        for k, x in v.items():
            if not isinstance(k, ATOMS):
                return _SKIP
            s = _safe(x, depth + 1)
            if s is _SKIP:
                return _SKIP
            out[str(k)] = s
        return out
    return _SKIP


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
    steps = []
    prev = {}
    pending = first  # the line whose effects we haven't emitted yet

    def emit(lineno, ops):
        steps.append({"line": lineno - first, "note": notes.get(lineno), "ops": ops})

    def record(lineno, loc):
        # A line event fires *before* the line runs, so the state we see is the
        # result of the previous line. Attribute it there.
        nonlocal prev, pending
        if len(steps) >= MAX_STEPS:
            return
        snap = {
            k: s
            for k, v in loc.items()
            if not k.startswith("_") and (s := _safe(v)) is not _SKIP
        }
        ops = []
        _diff([], prev, snap, ops)
        emit(pending, ops)
        prev = snap
        pending = lineno

    def local_trace(frame, event, arg):
        if event in ("line", "return"):
            record(frame.f_lineno, frame.f_locals)
        return local_trace

    def global_trace(frame, event, arg):
        return local_trace if event == "call" and frame.f_code is code else None

    sys.settrace(global_trace)
    try:
        result = fn(**args)
    finally:
        sys.settrace(None)

    if steps and steps[-1]["line"] != pending - first:
        emit(pending, [])  # land on the returning line
    if len(steps) >= MAX_STEPS:
        raise RuntimeError(f"{fn.__name__} exceeded {MAX_STEPS} steps")
    # Narration renders separately: drop the `#>` lines and renumber the steps.
    keep = [i for i, l in enumerate(src) if not l.strip().startswith("#>")]
    remap = {old: new for new, old in enumerate(keep)}
    for s in steps:
        s["line"] = remap[s["line"]]
    return steps, _safe(result), [src[i].split("#>")[0].rstrip() for i in keep]


def build_problem(mod):
    """Turn a solution module (META / VARIANTS / APPROACHES) into a trace file."""
    approaches = []
    for a in mod.APPROACHES:
        variants = []
        for v in mod.VARIANTS:
            steps, result, src = trace(a["fn"], v["input"])
            variants.append(
                {
                    "id": v["id"],
                    "label": v["label"],
                    "input": _safe(v["input"]),
                    "result": result,
                    "steps": steps,
                }
            )
        approaches.append(
            {
                "id": a["id"],
                "label": a["label"],
                "complexity": a["complexity"],
                "viz": a.get("viz", {}),
                "source": src,
                "variants": variants,
            }
        )
    return {"schemaVersion": SCHEMA_VERSION, **mod.META, "approaches": approaches}


def dump(obj, path):
    path.write_text(json.dumps(obj, separators=(",", ":")))
