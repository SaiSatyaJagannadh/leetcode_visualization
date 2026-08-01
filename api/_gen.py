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

# A reasoning model spends this budget on thinking *before* it writes a token of
# JSON, and those tokens are invisible in the response but count against the cap.
# At 16000 a full trace — two approaches, three variants each, narrated — was
# being cut off mid-stream on gemini-2.5-flash, which reads as "output token cap
# reached" rather than as a too-small cap. This is under every configured model's
# output limit; raise it per deployment if a model is chattier still.
MAX_OUTPUT_TOKENS = int(os.environ.get("SOLVE_MAX_OUTPUT_TOKENS", "32000"))
MAX_REPAIRS = 2  # hard stop, per the model ladder
# A congested NIM free tier answers in 125-180s, so the old hard-coded 180s read
# timeout cut off legitimate replies. Budget math worth knowing: this must stay
# under vercel.json maxDuration, and maxDuration must cover attempts x timeout,
# so a slow provider and a full repair ladder cannot both fit in one request.
CALL_TIMEOUT = int(os.environ.get("SOLVE_CALL_TIMEOUT", "420"))
# Total wall clock the repair ladder may spend. Keep it under vercel.json
# maxDuration or the platform kills the request instead. Note Vercel Hobby caps
# functions at 60s, so a provider that needs 40s+ per call cannot serve /solve
# there at all — that needs a faster model or an async job, not a bigger number.
BUDGET = int(os.environ.get("SOLVE_TIME_BUDGET", "400"))

# Per-million-token prices. Unset means we cannot price a call, and an unpriced
# call would make the monthly cap meaningless — so fall back to the flat
# placeholder cost rather than to zero.
PRICE_IN = float(os.environ.get("SOLVE_PRICE_IN_PER_MTOK", "0"))
PRICE_CACHED_IN = float(os.environ.get("SOLVE_PRICE_CACHED_IN_PER_MTOK", "0"))
PRICE_OUT = float(os.environ.get("SOLVE_PRICE_OUT_PER_MTOK", "0"))


# Marks a complaint as "thin content" rather than "structurally broken". A thin
# trace still replays correctly in the player, so shipping it beats returning a
# 502 — enforcing two approaches as a hard failure turned a useful result into no
# result at all on heavy problems. Structural faults are never soft.
THIN = "[thin] "


class GenerationError(Exception):
    """Semantic failure the repair ladder could not fix. The reason never leaks a key.

    `retry` is False by default and that default is the rule: a trace that will
    not replay is not fixed by handing the same prompt to a weaker model. It is
    set only where nothing was produced at all — see the truncation case in
    call(), where the next provider's limits are genuinely different.
    """

    def __init__(self, message, retry=False):
        super().__init__(message)
        self.retry = retry


# --------------------------------------------------------------------------- #
# providers — OpenAI first, NVIDIA as the fallback when OpenAI won't serve
# --------------------------------------------------------------------------- #


class Provider:
    """An OpenAI-shaped chat-completions endpoint.

    NVIDIA NIM speaks the same wire protocol, so the transport is shared. What
    is NOT shared is `strict: true` — that is an OpenAI feature. On a provider
    without it the model is merely *asked* for schema-shaped JSON, so malformed
    JSON becomes possible again and has to be handled rather than assumed away.
    """

    __slots__ = ("id", "url", "env_key", "env_model", "strict")

    def __init__(self, pid, default_url, env_key, env_model, strict):
        self.id = pid
        self.url = (os.environ.get(f"{pid.upper()}_BASE_URL") or default_url) + "/chat/completions"
        self.env_key = env_key
        self.env_model = env_model
        self.strict = strict

    @property
    def key(self):
        return os.environ.get(self.env_key) or ""

    def model(self, role):
        """Every model name comes from the environment. There are no literals here."""
        return os.environ.get(f"{self.env_model}_{role}") or ""

    def ready(self, role):
        return bool(self.key and self.model(role))


OPENAI = Provider("openai", "https://api.openai.com/v1", "OPENAI_API_KEY", "OPENAI_MODEL", True)
# NVIDIA NIM's OpenAI-compatible endpoint. Keys are `nvapi-…`, which is why the
# redactor in _lib matches that prefix too — a leak here is as bad as an sk- one.
NVIDIA = Provider(
    "nvidia", "https://integrate.api.nvidia.com/v1", "NVIDIA_API_KEY", "NVIDIA_MODEL", False
)
# Gemini's OpenAI-compatible endpoint. Keys are `AIza…`, also in the redactor.
GOOGLE = Provider(
    "google",
    "https://generativelanguage.googleapis.com/v1beta/openai",
    "GEMINI_API_KEY",
    "GEMINI_MODEL",
    False,
)

_ALL = {p.id: p for p in (OPENAI, NVIDIA, GOOGLE)}
# Order matters and the right order depends on which accounts are funded, so it
# is configuration rather than a code edit. Measured round-trips on a trivial
# schema request: gemini-2.5-flash 0.9s, NIM gpt-oss-20b 5-180s depending on
# congestion. Put the fast, funded one early.
ORDER = [
    s.strip()
    for s in (os.environ.get("SOLVE_PROVIDER_ORDER") or "openai,google,nvidia").split(",")
    if s.strip() in _ALL
]


def chain(role):
    """Providers to try for this role, in ORDER, skipping any that lack a key or
    a model name. The first one is the primary; the rest are fallbacks, so a
    healthy primary never silently downgrades."""
    return [_ALL[i] for i in ORDER if _ALL[i].ready(role) and _ALL[i].id not in _DEAD]


# A provider whose account is empty will be empty on the next request too, so
# remembering it turns two wasted round-trips per request into zero. Only
# terminal billing states go in here — a rate limit or a 5xx is temporary and
# must keep being retried.
_DEAD = {}
_TERMINAL = ("insufficient_quota", "credit_balance_exhausted", "billing_hard_limit_reached")


def _mark_if_dead(prov, e):
    code = getattr(e, "api_code", "") or ""
    if code in _TERMINAL:
        if prov.id not in _DEAD:
            log(f"{prov.id} reports {code}; skipping it until this process restarts")
        _DEAD[prov.id] = code


def _retryable(e):
    """Worth trying the next provider: rate limits and upstream faults only.

    HTTPError subclasses URLError, so it must be tested first — otherwise a 400
    (our malformed request) would fail over and get misreported as an outage.
    A semantic GenerationError is never retryable either: if a trace will not
    replay, a weaker model is not the fix and would just double the bill. The
    one exception carries its own flag, because "the model stopped mid-trace"
    and "the model finished and was wrong" are different facts.
    """
    if isinstance(e, GenerationError):
        return e.retry
    if isinstance(e, urllib.error.HTTPError):
        return e.code in (429, 500, 502, 503, 504)
    return isinstance(e, (urllib.error.URLError, TimeoutError))


def model(role):
    """Back-compat shim: the first configured provider's name for this role."""
    c = chain(role)
    return c[0].model(role) if c else ""


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


def _post(payload, key, url, timeout=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout or CALL_TIMEOUT, context=_SSL) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        # Both arrive as 429, and the difference is the whole story:
        # rate_limit_exceeded clears on its own, insufficient_quota never does.
        # Only the machine-readable code is kept — the prose can quote the key.
        try:
            e.api_code = ((json.loads(e.read().decode()) or {}).get("error") or {}).get("code") or ""
        except Exception:  # noqa: BLE001 — a body we cannot parse must not mask the HTTP error
            e.api_code = ""
        raise


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


def call(role, msgs, key, art, byo=None, prov=OPENAI):
    """One structured-output call. Returns (wire dict, usage)."""
    name = prov.model(role)
    if not name:
        raise GenerationError(f"{prov.env_model}_{role} is not configured")
    started = time.time()
    schema = {"type": "json_schema", "json_schema": _strip_x(art)}
    if not prov.strict:
        # NIM honours json_schema on many models but does not guarantee strict,
        # so the schema is a request here, not a contract. Handled below.
        schema["json_schema"] = {**schema["json_schema"], "strict": False}
    raw = _post(
        {
            "model": name,
            "messages": msgs,
            "max_completion_tokens": MAX_OUTPUT_TOKENS,
            "response_format": schema,
        },
        key,
        prov.url,
    )
    choice = (raw.get("choices") or [{}])[0]
    if choice.get("finish_reason") == "length":
        # Not a trace that will not replay — no trace at all. How much of the cap
        # a model spends on hidden reasoning before it writes a token of JSON
        # differs per model, so the next provider in the chain is a real fix
        # rather than a downgrade. This is the only retryable GenerationError.
        raise GenerationError(
            f"{prov.id}/{name} stopped at the {MAX_OUTPUT_TOKENS}-token output cap "
            "before the trace finished",
            retry=True,
        )
    if (choice.get("message") or {}).get("refusal"):
        raise GenerationError("model refused the request")
    u = _usage(raw)
    log(
        f"{role} provider={prov.id} model={name} prompt={u['prompt']} "
        f"cached_tokens={u['cached']} out_total={u['out_total']} "
        f"out_visible={u['out_visible']} reasoning={u['reasoning']} "
        f"{time.time() - started:.1f}s",
        byo,
    )
    body = (choice.get("message") or {}).get("content")
    if body is None:
        # Some NIM models answer with content: null and put everything in
        # reasoning_content. json.loads(None) raises a TypeError that reads like
        # a bug in the decoder, so name the real cause and let repair retry.
        raise GenerationError(f"{prov.id}/{name} returned no content")
    if prov.strict:
        # Strict mode makes malformed JSON structurally impossible. There is
        # deliberately no parse-and-retry here: a fallback would hide a real bug.
        return json.loads(body), u
    # Without strict, bad JSON is a normal outcome rather than a defect. Raise so
    # the existing repair ladder re-prompts, instead of silently retrying here —
    # that keeps one recovery mechanism, not two.
    try:
        return json.loads(body), u
    except ValueError as e:
        raise GenerationError(f"{prov.id} returned unparseable JSON: {e}") from e


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


def land_on_return(problem):
    """Append a final no-op step on the return line where a variant stops short.

    Not a fabrication and not a way to dodge validation. The player highlights
    `step.line`; a variant whose last step sits on the assignment *before* the
    return has correct state but never shows the return being reached. That step
    carries no ops, so it changes no state — and the result-equality check below
    still runs against that unchanged state, so a genuinely wrong trace still
    fails. Doing it here saves a repair round that costs 240s on a slow provider
    for something derivable from the source listing.
    """
    fixed = 0
    for a in problem.get("approaches") or []:
        source = a.get("source") or []
        rets = [i for i, ln in enumerate(source) if _RETURNS.match(ln.strip())]
        if not rets:
            continue
        for v in a.get("variants") or []:
            steps = v.get("steps") or []
            if not steps:
                continue
            end = steps[-1].get("line")
            if isinstance(end, (int, float)) and int(end) in rets:
                continue  # already lands on a return
            # The last return at or after where it stopped, else the final one.
            after = [i for i in rets if isinstance(end, (int, float)) and i >= int(end)]
            steps.append({"line": (after[0] if after else rets[-1]), "note": None, "ops": []})
            fixed += 1
    if fixed:
        log(f"landed {fixed} variant(s) on their return line without a repair round")
    return problem


_SEED_NUMS = None
_SEED_BY_NUM = {}


def fix_leetcode_number(problem):
    """Correct a hallucinated LeetCode number against pipeline/seed.py.

    The model guessed 1 for Move Zeroes, which would have pointed the outbound
    "LeetCode" link at Two Sum. seed.py holds 150 authoritative (title, number)
    pairs, so when the generated title matches one, the seed wins. A title we do
    not know stays unverified — a possibly-right number is more useful than none,
    and this only overrides where we can prove the model wrong.
    """
    global _SEED_NUMS
    if _SEED_NUMS is None:
        try:
            import seed  # pipeline/ is on sys.path via _lib

            _SEED_NUMS = {t.casefold(): n for _, t, _, _, n, _, _, _ in seed.rows()}
            _SEED_BY_NUM.update({n: t.casefold() for _, t, _, _, n, _, _, _ in seed.rows()})
        except Exception:  # noqa: BLE001 — a missing seed must not fail generation
            _SEED_NUMS = {}
    title = (problem.get("title") or "").strip().casefold()
    got = problem.get("leetcode")
    want = _SEED_NUMS.get(title)
    if want and got != want:
        log(f"corrected leetcode number for {title!r}: {got} -> {want}")
        problem["leetcode"] = want
        return problem
    # Reverse check, for the many problems outside the 150-problem seed. If the
    # number belongs to a DIFFERENT problem we do know, it is provably wrong —
    # Move Zeroes came back as 1, which is Two Sum, and would have linked there.
    # Drop it: the page renders without a LeetCode chip, which beats a link that
    # confidently sends the reader to the wrong problem.
    if not want and got and _SEED_BY_NUM.get(got, title) != title:
        log(f"dropped leetcode {got} from {title!r}: that number is {_SEED_BY_NUM[got]!r}")
        # Pop, never set to None: the field is `z.number().optional()`, which
        # accepts an absent key but rejects a JSON null, so assigning None here
        # would fail zod in the browser instead of just hiding the chip.
        problem.pop("leetcode", None)
    return problem


def validate(problem):
    """Replay every variant the way the player will and report what breaks.

    Mirrors lib/fold.ts `stateAt`. Two of these checks exist because strict mode
    dropped them: `.min(1)` on approaches/variants/steps is unrepresentable, so
    an empty array would reach zod in the browser instead.
    """
    bad = []
    if not problem.get("approaches"):
        bad.append("approaches is empty; at least one approach is required")
    # Content checks. The prompt asks for these and models skip them anyway, so
    # they are enforced here — the same lesson as the return-line rule. Messages
    # are fed verbatim into the repair turn, so they say what to add.
    #
    # Measured against the 150 authored traces before enforcing: 150/150 already
    # have >=2 examples, non-empty constraints and a non-empty prompt, so those
    # three checks only hold generated content to the existing house standard.
    # The two-approach rule is deliberately STRICTER than the corpus — 108 of the
    # 150 authored problems ship a single approach. That is content debt in the
    # corpus, not a reason to let new traces be thin; a generated trace with no
    # brute force cannot show why the clever version wins, which is the point.
    n_appr = len(problem.get("approaches") or [])
    if n_appr == 1:
        got = (problem["approaches"][0].get("label") or problem["approaches"][0].get("id") or "it")
        bad.append(
            f"{THIN}only one approach ({got}); add a second so the reader can compare. "
            "Put the obvious brute force first and the idiomatic solution second, "
            "both returning the same result for each variant id. If there is no "
            "slower version, give two honestly different strategies instead."
        )
    # An approach is a *strategy*; a variant is an *input*. Models confuse the two
    # axes, and the two-approach rule above made it worse: asked for more
    # approaches, gpt-oss-20b padded the array with entries called "Edge" and
    # "Worst case" carrying one variant each, so the UI showed four approach tabs
    # and one variant tab. Measured across the authored corpus before enforcing:
    # all 192 approaches carry exactly 3 variants, no approach id is ever named
    # after a variant, and 0 of 150 problems have approaches that disagree on
    # variant ids. So both checks below are the existing house convention.
    VARIANT_WORDS = {"typical", "edge", "worst-case", "worst case", "best-case"}
    seen_sets = {
        tuple(v.get("id") for v in (a.get("variants") or []))
        for a in problem.get("approaches") or []
    }
    if len(seen_sets) > 1:
        bad.append(
            THIN + "the approaches do not share the same variant ids "
            f"({sorted(seen_sets)}); every approach must run the same inputs, or "
            "the reader cannot compare them side by side"
        )
    for a in problem.get("approaches") or []:
        if (a.get("id") or "").strip().casefold() in VARIANT_WORDS:
            bad.append(
                THIN + f"approach {a.get('id')!r} is named after a variant, not a strategy. "
                "An approach is a way of solving the problem (brute force, two "
                "pointers); a variant is an input case (typical, edge, worst-case). "
                "Move it into the variants array of a real approach."
            )
    n_ex = len(problem.get("examples") or [])
    if n_ex < 2:
        bad.append(
            f"{THIN}only {n_ex} worked example(s); add at least one more that shows an "
            "edge the reader would get wrong — a tie, an empty input, a duplicate."
        )
    if not (problem.get("constraints") or []):
        bad.append("constraints is empty; state the input bounds in your own words")
    if not (problem.get("prompt") or "").strip():
        bad.append("prompt is empty; restate the problem in your own words")
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
                    # This message is fed verbatim into the repair turn, so it
                    # says what to DO. Naming only the symptom made models
                    # re-emit a different non-return last line, burning all
                    # three attempts on the same mistake.
                    rets = [
                        i for i, ln in enumerate(source) if _RETURNS.match(ln.strip())
                    ]
                    where = (
                        f" Append a final step with line {rets[-1]} "
                        f"({json.dumps(source[rets[-1]].strip())})."
                        if rets
                        else " The source has no return line; add one."
                    )
                    bad.append(
                        f"{vid}: the last step is on {json.dumps(tail)}, which is not a "
                        f"return.{where} Every variant must end on the return that "
                        f"produces its result."
                    )
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
    total = {}
    # A bring-your-own key is an OpenAI key by contract, so it pins the provider.
    # Failing a BYO request over to NVIDIA would spend our credit on their behalf.
    provs = [OPENAI] if byo_key else chain("GENERATE")
    if not provs or (byo_key and not OPENAI.model("GENERATE")):
        return _offline(), (0.0 if byo_key else _lib.STUB_COST_USD), total

    art = artifact()
    msgs = messages(prompt, art)
    for i, prov in enumerate(provs):
        key = byo_key if byo_key else prov.key
        try:
            problem, cost = _ladder(prov, key, msgs, art, byo_key, total)
            # Which vendor actually served this month, so a silent, permanent
            # failover shows up on the dashboard instead of only in the logs.
            _lib.store.incr(f"prov:{_lib.month_key()}:{prov.id}")
            return problem, (0.0 if byo_key else cost), total
        except Exception as e:  # noqa: BLE001 — re-raised unless a fallback exists
            _mark_if_dead(prov, e)
            if not (i + 1 < len(provs) and _retryable(e)):
                raise
            log(
                f"{prov.id} unavailable ({type(e).__name__}"
                f"{getattr(e, 'code', '') and ' ' + str(e.code)}), "
                f"failing over to {provs[i + 1].id}",
                byo_key,
            )
    raise GenerationError("no provider produced a trace")  # pragma: no cover


def _ladder(prov, key, msgs, art, byo_key, total):
    """The repair ladder against one provider. Returns (problem, cost_usd).

    Tokens accumulate into `total` even on a failed attempt, because they were
    billed — a failover must not hide what the first provider already cost.
    """
    role, cost = "GENERATE", 0.0
    # MAX_REPAIRS is the attempt ceiling; wall clock is the real limit. A slow
    # provider can spend 200s on one attempt, and three of those fit in no
    # serverless request — so refuse to *start* an attempt that cannot finish,
    # rather than having it killed mid-flight and losing the work already done.
    deadline = time.time() + BUDGET
    took = 0.0
    thin_best = None
    for attempt in range(MAX_REPAIRS + 1):
        if attempt and time.time() + took > deadline:
            log(
                f"time budget spent after {attempt} attempt(s); "
                f"last took {took:.0f}s, not starting another",
                byo_key,
            )
            break
        t0 = time.time()
        try:
            wire, u = call(role, msgs, key, art, byo_key, prov)
        except GenerationError:
            # A repair turn that errors (no content, unparseable) must not lose a
            # good-enough trace from an earlier turn.
            if thin_best:
                problem, cost, bad = thin_best
                log(f"repair errored; shipping the thin trace held from attempt 1", byo_key)
                return problem, cost
            raise
        took = time.time() - t0
        _add(total, u)
        cost += _cost(u)  # a repair round costs real money; it is billed, not free
        problem = fix_leetcode_number(land_on_return(decode(wire, art)))
        bad = validate(problem)
        if not bad:
            return problem, cost
        if all(b.startswith(THIN) for b in bad):
            # Replays correctly, just thin. Hold it: a later attempt may improve
            # it, but if one errors out instead we must not throw away a working
            # trace and return a 502. That is exactly what happened before —
            # attempt 1 was valid-but-thin, the repair returned no content, and
            # the whole request failed with a good trace already in hand.
            thin_best = thin_best or (problem, cost, bad)
        log(f"validation failed (attempt {attempt + 1}/{MAX_REPAIRS + 1}): {'; '.join(bad[:4])}", byo_key)
        if attempt == MAX_REPAIRS:
            break
        role = "REPAIR" if prov.model("REPAIR") else "GENERATE"
        msgs = msgs + [
            {"role": "assistant", "content": json.dumps(wire, separators=(",", ":"))},
            {
                "role": "user",
                # Without the "keep everything else" clause the model regressed a
                # previous fix while making the next one — it added the second
                # approach, then dropped it again on the following turn. The
                # repair budget is 2, so one thrash cycle burns the whole thing.
                "content": (
                    "That trace does not replay. Return the WHOLE trace again with "
                    "exactly these problems fixed:\n- "
                    + "\n- ".join(bad[:20])
                    + "\n\nKeep everything that already worked. Do not remove or "
                    "rename any approach, variant, example or constraint you have "
                    "already written, and do not reduce their counts: at least two "
                    "approaches, three variants each, and two examples. Fixing one "
                    "problem by breaking another is not progress."
                ),
            },
        ]
    if thin_best:
        problem, cost, bad = thin_best
        log(f"shipping a thin trace: {'; '.join(b[len(THIN):] for b in bad)[:150]}", byo_key)
        return problem, cost
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
    for prov in chain("CHEAP"):
        name = prov.model("CHEAP")
        schema = {"type": "json_schema", "json_schema": _NORM_SCHEMA}
        if not prov.strict:
            schema["json_schema"] = {**_NORM_SCHEMA, "strict": False}
        try:
            raw = _post(
                {
                    "model": name,
                    "messages": [
                        {"role": "system", "content": _NORM_SYSTEM},
                        {"role": "user", "content": prompt[:4000]},
                    ],
                    "max_completion_tokens": 200,
                    "response_format": schema,
                },
                prov.key,
                prov.url,
                timeout=20,
            )
            u = _usage(raw)
            _lib.store.incr(f"norm:{_lib.month_key()}:usd", float(_cost(u)))
            log(
                f"CHEAP provider={prov.id} model={name} prompt={u['prompt']} "
                f"cached_tokens={u['cached']} out_total={u['out_total']}"
            )
            return json.loads(raw["choices"][0]["message"]["content"])["canonical"]
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError, IndexError) as e:
            _mark_if_dead(prov, e)
            log(f"normalize via {prov.id} failed: {type(e).__name__}")
    # Every provider missing or failing means a colder cache, never a 502.
    return None
