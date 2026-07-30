#!/usr/bin/env python3
"""Gate tests for /api/solve. No framework — asserts, like pipeline/check.py.

The important assertions here are about ORDER and about the BYO key. A test that
only checked status codes would pass with the gates shuffled, which is exactly
the bug this file exists to catch.
"""

import contextlib
import io
import os
import sys
import tempfile
import urllib.error
from pathlib import Path


@contextlib.contextmanager
def patched(mod, name, value):
    """Swap a module attribute for the duration of a block, then put it back."""
    old = getattr(mod, name)
    setattr(mod, name, value)
    try:
        yield
    finally:
        setattr(mod, name, old)

ROOT = Path(__file__).resolve().parent.parent

# _lib snapshots config at import time, so the environment is set up first.
KV_FILE = Path(tempfile.mkdtemp()) / "kv.json"
os.environ.update(
    KV_LOCAL_PATH=str(KV_FILE),
    SOLVE_FREE_PER_DAY="2",
    SOLVE_MONTHLY_USD_CAP="1.00",
    SOLVE_STUB_COST_USD="0.25",
    ADMIN_SECRET="test-secret",
)
os.environ.pop("TURNSTILE_SECRET", None)  # dev bypass; asserted separately
os.environ.pop("VERCEL_ENV", None)
os.environ.pop("KV_REST_API_URL", None)
os.environ.pop("KV_REST_API_TOKEN", None)
# Hermetic: a developer's real key in the shell must not make the suite bill.
for _k in ("OPENAI_API_KEY", "OPENAI_MODEL_CHEAP", "OPENAI_MODEL_GENERATE", "OPENAI_MODEL_REPAIR",
           "NVIDIA_API_KEY", "NVIDIA_MODEL_CHEAP", "NVIDIA_MODEL_GENERATE", "NVIDIA_MODEL_REPAIR"):
    os.environ.pop(_k, None)

sys.path.insert(0, str(ROOT / "api"))
import _lib  # noqa: E402

FULL = ["turnstile", "hash", "cache", "quota", "cap", "generate", "record"]
BYO_KEY = "sk-test-byokey-must-never-be-logged-000"
FAILS = []


def check(name, cond, detail=""):
    print(f"{'ok  ' if cond else 'FAIL'} {name}{'' if cond else '  ' + detail}")
    if not cond:
        FAILS.append(name)


def reset():
    KV_FILE.unlink(missing_ok=True)


def run(prompt, sid="s1", ip="10.0.0.1", byo=None, token="t"):
    """Returns (status, body, audit, stderr)."""
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        status, body, audit = _lib.solve(prompt, token, sid, ip, byo)
        _lib.log(f"solve {status} gates={'>'.join(audit)}", byo)
    return status, body, audit, err.getvalue()


def spend():
    return _lib.num(_lib.store.get(f"spend:{_lib.month_key()}"))


def quota(sid="s1", ip="10.0.0.1"):
    d = _lib.day_key()
    return (
        _lib.num(_lib.store.get(f"quota:s:{sid}:{d}")),
        _lib.num(_lib.store.get(f"quota:i:{_lib.anon(ip)}:{d}")),
    )


# --------------------------------------------------------------------------- #

# The API must be able to reach the one tracer; the real generator needs it.
reset()
import leetviz  # noqa: E402

check("api can import tracer/leetviz.py", hasattr(leetviz, "MAX_STEPS"))

# 1. Full pass runs every gate, in order.
status, body, audit, _ = run("Two Sum")
check("fresh generate -> 200", status == 200, str(status))
check("gate order on the full path", audit == FULL, str(audit))
check("fresh generate is not marked cached", body.get("cached") is False)
check("trace parses as a problem", body["trace"]["schemaVersion"] == 1)
check("spend recorded", spend() == 0.25, str(spend()))
check("quota decremented on both keys", quota() == (1.0, 1.0), str(quota()))

# 2. A cache HIT stops at the cache gate: no quota, no spend.
before_q, before_s = quota(), spend()
status, body, audit, _ = run("two   sum")  # normalises to the same hash
check("cache hit -> 200", status == 200, str(status))
check("cache hit stops after the cache gate", audit == FULL[:3], str(audit))
check("cache hit is marked cached", body.get("cached") is True)
check("cache hit does NOT decrement quota", quota() == before_q, str(quota()))
check("cache hit does NOT record spend", spend() == before_s, str(spend()))

# 3. Quota exhaustion is 402 and stops at the quota gate.
run("problem two")  # session s1 now at 2/2
status, body, audit, _ = run("problem three")
check("over quota -> 402", status == 402, str(status))
check("over quota stops after the quota gate", audit == FULL[:4], str(audit))
check("402 body describes the BYO path", body.get("byoKey", {}).get("header") == "x-byo-key")

# 4. Quota is keyed on the IP too — a fresh cookie on a spent IP is still blocked.
status, _, audit, _ = run("problem four", sid="s2")
check("fresh session on a spent IP is blocked", status == 402, str(status))
check("IP block stops at the quota gate", audit == FULL[:4], str(audit))

# 5. ...and on the session too — a fresh IP with a spent cookie is blocked.
status, _, _, _ = run("problem five", ip="10.0.0.99")
check("fresh IP on a spent session is blocked", status == 402, str(status))

# 6. A BYO key skips quota and cap, generates, and records no spend.
before_s = spend()
status, body, audit, err = run("problem six", byo=BYO_KEY)
check("BYO key over quota -> 200", status == 200, str(status))
check("BYO key still runs every gate in order", audit == FULL, str(audit))
check("BYO generation records no spend", spend() == before_s, str(spend()))
check("BYO key not in the response body", BYO_KEY not in str(body))
check("BYO key not in the logs", BYO_KEY not in err, err)
# ...and if some future line does log it by accident, the redactor still eats it.
leak = io.StringIO()
with contextlib.redirect_stderr(leak):
    _lib.log(f"oops key={BYO_KEY}", BYO_KEY)
check("an accidental key log is redacted", BYO_KEY not in leak.getvalue(), leak.getvalue())
check("redaction marker replaces it", "[redacted-key]" in leak.getvalue(), leak.getvalue())

# 7. Global cap: free tier off, BYO still works.
reset()
_lib.store.incr(f"spend:{_lib.month_key()}", 1.5)
status, body, audit, _ = run("capped prompt", sid="s3", ip="10.0.0.2")
check("over cap -> 503", status == 503, str(status))
check("cap stops after the cap gate", audit == FULL[:5], str(audit))
check("503 body is honest about the cap", body.get("capUsd") == 1.0 and "resets" in body)
status, _, audit, _ = run("capped prompt", sid="s3", ip="10.0.0.2", byo=BYO_KEY)
check("BYO key works past the cap", status == 200, str(status))

# 8. Turnstile is gate one: a failure means nothing else ran.
reset()
os.environ["TURNSTILE_SECRET"] = "x"  # forces a real verify, which fails with no token
status, _, audit, _ = run("blocked", token=None)
check("turnstile failure -> 403", status == 403, str(status))
check("turnstile failure stops at gate one", audit == ["turnstile"], str(audit))
del os.environ["TURNSTILE_SECRET"]

# 9. A missing prompt is rejected before any gate runs.
status, _, audit, _ = run("   ")
check("empty prompt -> 400 before any gate", status == 400 and audit == [], str(audit))

# 10. Redaction covers bare key shapes, not just the key we were handed.
check(
    "redact scrubs sk- keys",
    "[redacted-key]" in _lib.redact("boom: sk-abcdefghijklmnop"),
)
check("redact scrubs an exact non-sk secret", _lib.redact("k=hunter22hunter22", "hunter22hunter22") == "k=[redacted-key]")

# 11. Admin is closed without the secret and by the wrong secret.
check("admin rejects a missing secret", not _lib.admin_ok(None))
check("admin rejects a wrong secret", not _lib.admin_ok("nope"))
check("admin accepts the right secret", _lib.admin_ok("test-secret"))
check("spend report reads real counters", _lib.spend_report()["capUsd"] == 1.0)

# --------------------------------------------------------------------------- #
# 12. The generation layer. Everything below runs offline: `_gen.call` is the
#     only place an HTTP request happens and the repair test replaces it.
# --------------------------------------------------------------------------- #

import copy  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402

import _gen  # noqa: E402

ART = _gen.artifact()
TRACE = json.loads((ROOT / "traces" / "two-sum.json").read_text())

# 12a. The wire encoding is lossless. Optional keys, tuples and open maps are
# all rewritten for strict mode; a rewrite that does not round-trip is a trace
# the player cannot parse.
def same(a, b, path=""):
    """Equal, except that an optional key which was null may come back absent —
    zod treats those two as the same value, and dropping it is the canonical form."""
    if isinstance(a, dict) and isinstance(b, dict):
        for k in set(a) | set(b):
            if k not in b and a.get(k) is None:
                continue
            if k not in a or k not in b:
                return f"{path}/{k} appeared/vanished"
            bad = same(a[k], b[k], f"{path}/{k}")
            if bad:
                return bad
        return ""
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return f"{path} length {len(a)} -> {len(b)}"
        return next((m for m in (same(x, y, f"{path}/{i}") for i, (x, y) in enumerate(zip(a, b))) if m), "")
    return "" if a == b else f"{path}: {json.dumps(a)[:40]} -> {json.dumps(b)[:40]}"


roundtrip = []
for p in sorted((ROOT / "traces").glob("*.json")):
    if p.name == "index.json":
        continue
    t = json.loads(p.read_text())
    bad = same(t, _gen.decode(_gen.encode(t, ART), ART))
    if bad:
        roundtrip.append(f"{p.name}{bad}")
check("wire encoding round-trips every committed trace", not roundtrip, str(roundtrip[:3]))

wire = _gen.encode(TRACE, ART)
op = wire["approaches"][0]["variants"][0]["steps"][0]["ops"][0]
check("tuples are encoded positionally for strict mode", set(op) == {"_0", "_1", "_2"}, str(op)[:80])
check("maps are wrapped in $entries", set(wire["approaches"][0]["viz"]) == {"$entries"})
check("absent optional keys are explicit nulls", wire["unordered"] is None)
check("decoding drops the null again", "unordered" not in _gen.decode(wire, ART))

# 12b. Semantic validation: the real trace passes, three broken ones do not.
check("a committed trace passes semantic validation", _gen.validate(TRACE) == [], str(_gen.validate(TRACE)))


def broken(mutate):
    t = copy.deepcopy(TRACE)
    mutate(t["approaches"][0])
    return _gen.validate(t)


def _set_line(a):
    a["variants"][0]["steps"][0]["line"] = 99


def _dangle(a):
    a["variants"][0]["steps"][0]["ops"] = [["set", ["dp", 0, 1], 5]]


def _wrong_result(a):
    a["variants"][0]["result"] = ["nope"]
    a["source"] = a["source"][:-1] + ["    return total"]
    a["variants"][0]["steps"][-1]["line"] = len(a["source"]) - 1
    a["variants"][0]["steps"][-1]["ops"] = [["set", ["total"], 9]]


def _no_return(a):
    a["variants"][0]["steps"][-1]["line"] = 0


def _empty(a):
    a["variants"][0]["steps"] = []


check("line index out of range is caught", any("outside source" in m for m in broken(_set_line)))
check("a dangling op path is caught", any("does not exist yet" in m for m in broken(_dangle)))
check("a result the ops never reach is caught", any("disagree" in m for m in broken(_wrong_result)))
check("a trace that never returns is caught", any("not a return" in m for m in broken(_no_return)))
check("an empty steps array is caught", any("steps is empty" in m for m in broken(_empty)))

# 12c. A failing trace escalates to the repair model and stops at exactly 2
# repairs. This is the whole point of the ladder: without the hard stop a
# stubborn prompt bug bills forever.
os.environ.update(
    OPENAI_API_KEY="sk-test-not-a-real-key-000000",
    OPENAI_MODEL_GENERATE="test-generate",
    OPENAI_MODEL_REPAIR="test-repair",
)
calls = []
# A trace whose ops end on `return total` with total=9 while claiming the result
# is ["definitely wrong"]: it parses, it replays, and it is still wrong.
_broken = copy.deepcopy(TRACE)
_a = _broken["approaches"][0]
_a["source"] = _a["source"] + ["    return total"]
_a["variants"] = _a["variants"][:1]
_a["variants"][0]["result"] = ["definitely wrong"]
_a["variants"][0]["steps"] = [
    {"line": 0, "note": None, "ops": [["set", ["total"], 9]]},
    {"line": len(_a["source"]) - 1, "note": None, "ops": []},
]
bad_wire = _gen.encode(_broken, ART)
check("the repair fixture really is invalid", _gen.validate(_broken) != [])


def fake_call(role, msgs, key, art, byo=None, prov=None):
    calls.append((role, len(msgs)))
    return bad_wire, {"prompt": 10, "cached": 0, "out_total": 5, "out_visible": 5, "reasoning": 0}


_gen.call = fake_call
try:
    _gen.generate("always broken")
    raised = ""
except _gen.GenerationError as e:
    raised = str(e)

check("a semantically broken trace raises rather than shipping", bool(raised), raised)
check("repair runs exactly twice then hard-stops", len(calls) == 3, str(calls))
check("the ladder is generate -> repair -> repair",
      [r for r, _ in calls] == ["GENERATE", "REPAIR", "REPAIR"], str(calls))
check("each repair turn appends to the conversation, never rewrites the prefix",
      [n for _, n in calls] == [3, 5, 7], str(calls))

# ...and the gate chain turns that into a clean 502 with no spend and no cache entry.
reset()
before_s = spend()
status, body, audit, err = run("always broken", sid="s9", ip="10.0.0.9", byo=BYO_KEY)
check("a hard-stopped generation is 502", status == 502, str(status))
check("502 stops after the generate gate", audit == FULL[:6], str(audit))
check("502 records no spend", spend() == before_s, str(spend()))
check("502 body says nothing about the model", "repair" not in str(body).lower(), str(body))
_gen.call = None  # any further live call is a bug, not a network hiccup

# 12d. Prompt order. The static blocks must be byte-identical between two
# different requests or OpenAI's prefix cache never hits and every call pays
# full price for the same 2 kB of instructions.
one = _gen.messages("Reverse a linked list", ART)
two = _gen.messages("Merge k sorted lists", ART)
check("the user's problem is the LAST message", one[-1]["role"] == "user")
check("the static prefix is identical across requests", one[:-1] == two[:-1])
check("the problem text never reaches the system prompt",
      "Reverse a linked list" not in "".join(m["content"] for m in one[:-1]))
check("the static prefix carries no per-request value",
      not re.search(r"\b(19|20)\d{2}-\d\d-\d\dT|request[-_ ]?id", one[0]["content"] + one[1]["content"]))
check("the exemplar is in wire form, so the few-shot cannot drift",
      '"_0":"set"' in one[1]["content"].replace(" ", ""))
check("the prompt is versioned", re.fullmatch(r"[0-9a-f]{12}", _gen.prompt_version()) is not None)

# 12e. No hardcoded model names: every one comes from the environment.
check("model names come from env only", _gen.model("GENERATE") == "test-generate")
for _k in ("OPENAI_API_KEY", "OPENAI_MODEL_GENERATE", "OPENAI_MODEL_REPAIR"):
    os.environ.pop(_k, None)
check("no model configured -> offline dev generator, not a crash",
      _gen.generate("anything")[0]["schemaVersion"] == 1)

# 12f. The report carries the numbers the owner asked for.
rep = _lib.spend_report()
for field in ("outputTokensMonthBilled", "outputTokensMonthVisible", "reasoningTokensMonth",
              "cachedPromptTokensMonth", "promptVersion", "normalizeSpendMonthUsd"):
    check(f"/admin/spend reports {field}", field in rep, str(sorted(rep)))


# 13. Provider failover: OpenAI first, NVIDIA only when OpenAI won't serve.
os.environ.update(OPENAI_API_KEY="sk-openai-test-key-000000", OPENAI_MODEL_GENERATE="oai-model",
                  NVIDIA_API_KEY="nvapi-test-key-00000000000", NVIDIA_MODEL_GENERATE="nv-model")

check("chain is openai then nvidia, never the reverse",
      [p.id for p in _gen.chain("GENERATE")] == ["openai", "nvidia"])

_HTTP = lambda code: urllib.error.HTTPError("u", code, "boom", {}, None)
_GOOD = json.loads((ROOT / "traces" / "two-sum.json").read_text())

def _fake(fail_on, record):
    """Stand in for _gen.call: fails for one provider, succeeds for the other."""
    def call(role, msgs, key, art, byo=None, prov=_gen.OPENAI):
        record.append(prov.id)
        if prov.id == fail_on:
            raise fail_on_error[0]
        return _gen.encode(_GOOD), {"prompt": 1, "cached": 0, "out_total": 1,
                                    "out_visible": 1, "reasoning": 0, "calls": 1}
    return call

fail_on_error = [_HTTP(429)]
seen = []
with patched(_gen, "call", _fake("openai", seen)):
    prob, _, _ = _gen.generate("reverse a linked list")
check("429 on openai fails over to nvidia", seen == ["openai", "nvidia"], str(seen))
check("the failover still returns a valid trace", prob["schemaVersion"] == 1)

fail_on_error = [_HTTP(400)]
seen = []
try:
    with patched(_gen, "call", _fake("openai", seen)):
        _gen.generate("reverse a linked list")
    raised = False
except urllib.error.HTTPError:
    raised = True
check("400 surfaces instead of failing over (it is our bug)", raised and seen == ["openai"], str(seen))

fail_on_error = [_gen.GenerationError("will not replay")]
seen = []
try:
    with patched(_gen, "call", _fake("openai", seen)):
        _gen.generate("reverse a linked list")
except _gen.GenerationError:
    pass
check("a semantic failure does not fail over to a weaker model", seen == ["openai"], str(seen))

fail_on_error = [_HTTP(429)]
seen = []
try:
    with patched(_gen, "call", _fake("openai", seen)):
        _gen.generate("reverse a linked list", byo_key=BYO_KEY)
except urllib.error.HTTPError:
    pass
check("a BYO key never fails over to our NVIDIA credit", seen == ["openai"], str(seen))

# 13b. nvapi- keys must redact exactly like sk- ones.
check("redact() scrubs an nvapi- key",
      "nvapi-" not in _lib.redact("boom nvapi-abcdefgh12345678 boom"),
      _lib.redact("boom nvapi-abcdefgh12345678 boom"))
check("redact() still scrubs an sk- key",
      "sk-" not in _lib.redact(f"boom {BYO_KEY} boom"))

rep = _lib.spend_report()
check("/admin/spend reports generationsByProvider", "generationsByProvider" in rep)
check("/admin/spend reports the live provider chain",
      rep.get("providerChain") == ["openai", "nvidia"], str(rep.get("providerChain")))

for _k in ("NVIDIA_API_KEY", "NVIDIA_MODEL_GENERATE", "OPENAI_API_KEY", "OPENAI_MODEL_GENERATE"):
    os.environ.pop(_k, None)

reset()

print(f"\n{len(FAILS)} failures")
sys.exit(1 if FAILS else 0)
