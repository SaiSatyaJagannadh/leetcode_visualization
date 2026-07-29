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
from pathlib import Path

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

reset()
print(f"\n{len(FAILS)} failures")
sys.exit(1 if FAILS else 0)
