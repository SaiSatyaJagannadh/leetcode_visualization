"""The generation layer: prompt, structured-output call, decode, validate, repair.

`_lib.py` owns the gate chain; this module owns what happens inside the one
`generate` gate. It is imported lazily from `_lib` so the import cycle stays
one-directional and `/api/admin/spend` never pays for it.

Three things here are load-bearing and easy to quietly break:

1. **Prompt order.** system (static) -> context (static) -> the user's problem,
   LAST. Nothing per-request may precede the static blocks: a request id or a
   timestamp in front of them changes the prefix on every call and OpenAI's
   automatic prompt cache never hits. `cached_tokens` is logged per call so the
   regression is visible rather than merely expensive.

2. **The wire encoding.** `prompts/solve-schema.json` is derived from
   lib/schema.ts by `pipeline/schema-json.mts`; it is never hand-edited. Strict
   mode cannot express optional keys, tuples or open maps, so the transform
   rewrites them and `_wire(..., enc=False)` reverses each rewrite, driven by
   the same artifact. Neither side hand-lists a field.

3. **No generated code is executed.** The model emits the trace itself, so there
   is nothing to run and no sandbox. Validation replays ops as data.
"""

import hashlib
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.request

import _lib
from _lib import ROOT, log

PROMPT_FILE = ROOT / "prompts" / "solve-system.md"
SCHEMA_FILE = ROOT / "prompts" / "solve-schema.json"
EXEMPLAR = ROOT / "traces" / "two-sum.json"
SPLIT = "---8<--- context"

API_URL = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1") + "/chat/completions"
MAX_OUTPUT_TOKENS = int(os.environ.get("SOLVE_MAX_OUTPUT_TOKENS", "16000"))
MAX_REPAIRS = 2  # hard stop, per the model ladder

# Per-million-token prices. Unset means we cannot price a call, and an unpriced
# call would make the monthly cap meaningless — so fall back to the flat
# placeholder cost rather than to zero.
PRICE_IN = float(os.environ.get("SOLVE_PRICE_IN_PER_MTOK", "0"))
PRICE_CACHED_IN = float(os.environ.get("SOLVE_PRICE_CACHED_IN_PER_MTOK", "0"))
PRICE_OUT = float(os.environ.get("SOLVE_PRICE_OUT_PER_MTOK", "0"))


class GenerationError(Exception):
    """Semantic failure the repair ladder could not fix. The reason never leaks a key."""


def model(role):
    """Every model name comes from the environment. There are no literals here."""
    return os.environ.get(f"OPENAI_MODEL_{role}") or ""


# --------------------------------------------------------------------------- #
# the derived schema, and the encoding it forces
# --------------------------------------------------------------------------- #


def artifact():
    return json.loads(SCHEMA_FILE.read_text())


def _strip_x(node):
    """`x-optional` is ours, not JSON Schema's. It never reaches the API."""
    if isinstance(node, dict):
        return {k: _strip_x(v) for k, v in node.items() if not k.startswith("x-")}
    if isinstance(node, list):
        return [_strip_x(v) for v in node]
    return node


def _resolve(sch, root):
    while "$ref" in sch:
        sch = root["$defs"][sch["$ref"].rsplit("/", 1)[-1]]
    return sch


def _types(sch):
    t = sch.get("type")
    return {t} if isinstance(t, str) else set(t or ())


def _is_record(sch):
    return set(sch.get("properties") or ()) == {"$entries"}


def _is_tuple(sch):
    p = sch.get("properties") or {}
    return bool(p) and all(re.fullmatch(r"_\d+", k) for k in p)


def _pick(options, data, enc, root):
    """Choose the union branch for this value. Unambiguous by construction:
    a map is always wrapped in `$entries`, so it can never be mistaken for a
    plain array of two-key objects."""
    cands = [_resolve(o, root) for o in options]
    if isinstance(data, bool):
        want = "boolean"
    elif isinstance(data, (int, float)):
        want = "number"
    elif isinstance(data, str):
        want = "string"
    elif isinstance(data, list):
        arr = [c for c in cands if "array" in _types(c)]
        if arr and not (enc and any(_is_tuple(c) for c in cands)):
            return arr[0]
        want = "object" if enc else "array"
        if want == "array":
            return arr[0] if arr else cands[0]
    else:
        want = "object"

    if want == "object":
        objs = [c for c in cands if "object" in _types(c)] or cands
        if len(objs) == 1:
            return objs[0]
        for c in objs:  # sibling tuples (set vs del) differ by arity and head literal
            p = c.get("properties") or {}
            if enc:
                head = (p.get("_0") or {}).get("enum")
                if len(p) == len(data) and (head is None or data[0] in head):
                    return c
            elif set(p) == set(data):
                return c
        return objs[0]
    for c in cands:
        if want in _types(c):
            return c
    return cands[0]


def _wire(sch, data, enc, root):
    """schemaVersion-1 value <-> strict-mode wire value. One walker, both ways."""
    sch = _resolve(sch, root)
    if data is None:
        return None
    if "anyOf" in sch:
        sch = _pick(sch["anyOf"], data, enc, root)
    t = _types(sch)

    if "object" in t and "properties" in sch:
        props = sch["properties"]
        if _is_record(sch):
            vs = props["$entries"]["items"]["properties"]["value"]
            if enc:
                return {
                    "$entries": [
                        {"key": str(k), "value": _wire(vs, v, True, root)} for k, v in data.items()
                    ]
                }
            return {e["key"]: _wire(vs, e["value"], False, root) for e in data.get("$entries") or []}
        if _is_tuple(sch):
            if enc:
                return {f"_{i}": _wire(props[f"_{i}"], v, True, root) for i, v in enumerate(data)}
            return [
                _wire(props[f"_{i}"], data.get(f"_{i}"), False, root)
                for i in range(len(props))
                if f"_{i}" in data
            ]
        out = {}
        for k, ks in props.items():
            v = data.get(k)
            # A key the frozen schema calls optional came back null: drop it,
            # or zod rejects the null the strict schema was obliged to allow.
            # `.nullish()` accepts either, so dropping is the canonical form.
            if not enc and v is None and ks.get("x-optional"):
                continue
            out[k] = _wire(ks, v, enc, root)
        return out

    if "array" in t and isinstance(data, list):
        return [_wire(sch["items"], v, enc, root) for v in data]
    return data


def encode(problem, art=None):
    art = art or artifact()
    return _wire(art["schema"], problem, True, art["schema"])


def decode(wire, art=None):
    art = art or artifact()
    return _wire(art["schema"], wire, False, art["schema"])


# --------------------------------------------------------------------------- #
# prompt: static blocks first, the user's problem last
# --------------------------------------------------------------------------- #


def prompt_version():
    """Content hash. A bad generation names the exact prompt that produced it,
    and iterating the file needs no redeploy and no version bookkeeping."""
    try:
        return hashlib.sha256(PROMPT_FILE.read_bytes()).hexdigest()[:12]
    except OSError:
        return "missing"


def _exemplar(art):
    """The few-shot, built by encoding a committed trace rather than by hand —
    a hand-written exemplar drifts the moment the encoding changes."""
    p = json.loads(EXEMPLAR.read_text())
    a = dict(p["approaches"][0])
    a["variants"] = a["variants"][:1]
    p = {**p, "approaches": [a]}
    return json.dumps(encode(p, art), separators=(",", ":"))


def messages(problem_text, art):
    """Order is the whole cost story: static, static, then the user. Read at
    request time so prompts/solve-system.md can be edited without a redeploy."""
    text = PROMPT_FILE.read_text()
    system, _, context = text.partition(SPLIT)
    return [
        {"role": "system", "content": system.strip()},
        {"role": "system", "content": f"{context.strip()}\n\n{_exemplar(art)}"},
        {"role": "user", "content": problem_text},
    ]


# --------------------------------------------------------------------------- #
# the call
# --------------------------------------------------------------------------- #


def _ssl_context():
    """A python.org macOS build ships no CA bundle until someone runs
    Install Certificates.command, so every HTTPS call dies with
    CERTIFICATE_VERIFY_FAILED. Prefer certifi's bundle when it is importable;
    fall back to the system default, which is what Vercel's Linux runtime uses.
    Never disable verification — an unverified call to an API we send a key to
    is worse than a failing one."""
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


_SSL = _ssl_context()


def _post(payload, key, timeout=180):
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout, context=_SSL) as r:
        return json.load(r)


def _usage(raw):
    """Reasoning tokens bill as output but never appear in the response, so the
    visible count is not the billed count. Both are reported, never conflated."""
    u = raw.get("usage") or {}
    total_out = int(u.get("completion_tokens") or 0)
    reasoning = int((u.get("completion_tokens_details") or {}).get("reasoning_tokens") or 0)
    return {
        "prompt": int(u.get("prompt_tokens") or 0),
        "cached": int((u.get("prompt_tokens_details") or {}).get("cached_tokens") or 0),
        "out_total": total_out,
        "out_visible": max(0, total_out - reasoning),
        "reasoning": reasoning,
    }


def _cost(u):
    if not (PRICE_IN or PRICE_OUT or PRICE_CACHED_IN):
        return _lib.STUB_COST_USD
    fresh = max(0, u["prompt"] - u["cached"])
    return (
        fresh * PRICE_IN + u["cached"] * PRICE_CACHED_IN + u["out_total"] * PRICE_OUT
    ) / 1_000_000


def _add(into, u):
    for k, v in u.items():
        into[k] = into.get(k, 0) + v
    into["calls"] = into.get("calls", 0) + 1


def call(role, msgs, key, art, byo=None):
    """One structured-output call. Returns (wire dict, usage)."""
    name = model(role)
    if not name:
        raise GenerationError(f"OPENAI_MODEL_{role} is not configured")
    started = time.time()
    raw = _post(
        {
            "model": name,
            "messages": msgs,
            "max_completion_tokens": MAX_OUTPUT_TOKENS,
            "response_format": {"type": "json_schema", "json_schema": _strip_x(art)},
        },
        key,
    )
    choice = (raw.get("choices") or [{}])[0]
    if choice.get("finish_reason") == "length":
        raise GenerationError("output token cap reached before the trace finished")
    if (choice.get("message") or {}).get("refusal"):
        raise GenerationError("model refused the request")
    u = _usage(raw)
    log(
        f"{role} model={name} prompt={u['prompt']} cached_tokens={u['cached']} "
        f"out_total={u['out_total']} out_visible={u['out_visible']} "
        f"reasoning={u['reasoning']} {time.time() - started:.1f}s",
        byo,
    )
    # Strict mode makes malformed JSON structurally impossible. There is
    # deliberately no parse-and-retry here: a fallback would hide a real bug.
    return json.loads(choice["message"]["content"]), u


# --------------------------------------------------------------------------- #
# semantic validation — the only kind of failure strict mode leaves possible
# --------------------------------------------------------------------------- #


def _child(node, key):
    """One deref, matching lib/fold.ts `node[key]`: a miss is a crash there too."""
    if isinstance(node, list):
        i = int(key)
        if not 0 <= i < len(node):
            raise KeyError(key)
        return node[i]
    if isinstance(node, dict):
        if str(key) not in node:
            raise KeyError(key)
        return node[str(key)]
    raise KeyError(key)


_RETURNS = re.compile(r"^return\b(.*)$")
_NAME = re.compile(r"[A-Za-z_]\w*\Z")
_KEYWORDS = {"True", "False", "None"}


def _has_ref(v):
    return '"$ref"' in json.dumps(v)


def validate(problem):
    """Replay every variant the way the player will and report what breaks.

    Mirrors lib/fold.ts `stateAt`. Two of these checks exist because strict mode
    dropped them: `.min(1)` on approaches/variants/steps is unrepresentable, so
    an empty array would reach zod in the browser instead.
    """
    bad = []
    if not problem.get("approaches"):
        bad.append("approaches is empty; at least one approach is required")
    for a in problem.get("approaches") or []:
        where = a.get("id") or "?"
        source = a.get("source") or []
        if not source:
            bad.append(f"{where}: source is empty")
        if not a.get("variants"):
            bad.append(f"{where}: variants is empty; at least one is required")
        for v in a.get("variants") or []:
            vid = f"{where}/{v.get('id') or '?'}"
            steps = v.get("steps") or []
            if not steps:
                bad.append(f"{vid}: steps is empty; at least one step is required")
                continue
            state = {}
            for n, s in enumerate(steps):
                line = s.get("line")
                if not isinstance(line, (int, float)) or not 0 <= int(line) < len(source):
                    bad.append(f"{vid} step {n}: line {line} is outside source (0..{len(source) - 1})")
                for op in s.get("ops") or []:
                    path = op[1] if len(op) > 1 else []
                    if not path:
                        bad.append(f"{vid} step {n}: op with an empty path")
                        continue
                    try:
                        node = state
                        for k in path[:-1]:
                            node = _child(node, k)
                        last = path[-1]
                        if op[0] == "del":
                            _child(node, last)
                            node.pop(str(last) if isinstance(node, dict) else int(last), None)
                        elif isinstance(node, list):
                            i = int(last)
                            while len(node) <= i:
                                node.append(None)
                            node[i] = op[2]
                        elif isinstance(node, dict):
                            node[str(last)] = op[2]
                        else:
                            raise KeyError(last)
                    except (KeyError, TypeError, ValueError, IndexError):
                        bad.append(
                            f"{vid} step {n}: op path {json.dumps(path)} does not exist yet; "
                            "every parent must be set before its child"
                        )
            end = steps[-1].get("line")
            if isinstance(end, (int, float)) and 0 <= int(end) < len(source):
                tail = source[int(end)].strip()
                m = _RETURNS.match(tail)
                if not m:
                    bad.append(f"{vid}: the last step is on {json.dumps(tail)}, not a return")
                else:
                    expr = m.group(1).strip()
                    # Only a bare name can be checked without executing anything,
                    # and nothing here executes model output. `$ref` values are
                    # object-graph handles, not comparable to a plain result.
                    if (
                        _NAME.fullmatch(expr)
                        and expr not in _KEYWORDS
                        and expr in state
                        and not _has_ref(state[expr])
                        and not _has_ref(v.get("result"))
                        and state[expr] != v.get("result")
                    ):
                        bad.append(
                            f"{vid}: returns {expr}={json.dumps(state[expr])} but result is "
                            f"{json.dumps(v.get('result'))}; the ops and the result disagree"
                        )
    return bad


# --------------------------------------------------------------------------- #
# generate
# --------------------------------------------------------------------------- #


def _offline():
    """No model configured: serve the committed trace so the gates stay testable
    without credentials. Loud, and refused outright in production — the same
    shape as the KV file-store shim, not a second generator."""
    if _lib.IS_PROD:
        raise GenerationError("OPENAI_MODEL_GENERATE / OPENAI_API_KEY are required in production")
    log("WARNING: no OPENAI_MODEL_GENERATE — serving the committed trace. Dev only.")
    return json.loads(EXEMPLAR.read_text())


def generate(prompt, byo_key=None):
    """Returns (problem, cost_usd, usage). Raises GenerationError on a hard stop.

    Repair is capped at MAX_REPAIRS. The repair turns are appended *after* the
    user's problem, so the static prefix — and its cache hit — survives them.
    """
    key = byo_key or os.environ.get("OPENAI_API_KEY")
    total = {}
    if not key or not model("GENERATE"):
        return _offline(), (0.0 if byo_key else _lib.STUB_COST_USD), total

    art = artifact()
    msgs = messages(prompt, art)
    role, cost = "GENERATE", 0.0
    for attempt in range(MAX_REPAIRS + 1):
        wire, u = call(role, msgs, key, art, byo_key)
        _add(total, u)
        cost += _cost(u)  # a repair round costs real money; it is billed, not free
        problem = decode(wire, art)
        bad = validate(problem)
        if not bad:
            return problem, (0.0 if byo_key else cost), total
        log(f"validation failed (attempt {attempt + 1}/{MAX_REPAIRS + 1}): {'; '.join(bad[:4])}", byo_key)
        if attempt == MAX_REPAIRS:
            break
        role = "REPAIR"
        msgs = msgs + [
            {"role": "assistant", "content": json.dumps(wire, separators=(",", ":"))},
            {
                "role": "user",
                "content": "That trace does not replay. Fix exactly these problems and "
                "return the whole trace again:\n- " + "\n- ".join(bad[:20]),
            },
        ]
    raise GenerationError(f"trace still does not replay after {MAX_REPAIRS} repair attempts")


# --------------------------------------------------------------------------- #
# normalize / classify — the cheap model, on the hash gate
# --------------------------------------------------------------------------- #

_NORM_SCHEMA = {
    "name": "canonical_problem",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {"canonical": {"type": "string"}},
        "required": ["canonical"],
        "additionalProperties": False,
    },
}
_NORM_SYSTEM = (
    "Name the classic algorithm problem the user is describing, as its canonical "
    "lowercase title and nothing else — 'two sum', 'reverse linked list'. If it is "
    "not a known problem, echo the request back with whitespace collapsed."
)


def canonical(prompt):
    """Canonical form for the cache key, or None if the cheap model is unavailable.

    Falls open on purpose: a normalisation outage must degrade to a colder cache,
    never to a 502. Its tokens are counted separately — see spend_report.
    """
    key, name = os.environ.get("OPENAI_API_KEY"), model("CHEAP")
    if not (key and name):
        return None
    try:
        raw = _post(
            {
                "model": name,
                "messages": [
                    {"role": "system", "content": _NORM_SYSTEM},
                    {"role": "user", "content": prompt[:4000]},
                ],
                "max_completion_tokens": 200,
                "response_format": {"type": "json_schema", "json_schema": _NORM_SCHEMA},
            },
            key,
            timeout=20,
        )
        u = _usage(raw)
        _lib.store.incr(f"norm:{_lib.month_key()}:usd", float(_cost(u)))
        log(f"CHEAP model={name} prompt={u['prompt']} cached_tokens={u['cached']} out_total={u['out_total']}")
        return json.loads(raw["choices"][0]["message"]["content"])["canonical"]
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, IndexError) as e:
        log(f"normalize failed, falling back to local canonicalisation: {type(e).__name__}")
        return None
