"""Server-side plumbing for /api: the KV client, the /solve gate chain, redaction.

Vercel does not route files whose basename starts with `_`, so the handlers can
import this but nothing can call it over HTTP.

The gate chain is the whole point of this module. No expensive operation may run
before every cheap gate has passed, so `solve()` is one flat sequence that
appends each gate it *enters* to an `audit` list. `pipeline/test_solve.py`
asserts on that list, so a reordering bug fails the test even when every status
code stays the same.

Generation itself lives in `_gen.py` — the prompt, the structured-output call,
the decode, the semantic validation and the repair ladder. This module still
decides *whether* it runs. `_gen` is imported lazily so the cycle stays
one-directional and `/api/admin/spend` never pays for it.
"""

import hashlib
import hmac
import json
import os
import re
import secrets
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# The real generator (next pass) traces candidate solutions with tracer/leetviz.py.
# There is one tracer; the API must reach it rather than grow a second one.
for _p in (str(ROOT / "tracer"), str(ROOT / "pipeline")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

IS_PROD = os.environ.get("VERCEL_ENV") == "production"
FREE_PER_DAY = int(os.environ.get("SOLVE_FREE_PER_DAY", "5"))
MONTHLY_CAP_USD = float(os.environ.get("SOLVE_MONTHLY_USD_CAP", "25"))
# Fallback unit cost, used when SOLVE_PRICE_*_PER_MTOK are unset and by the
# offline dev generator. An unpriced call must not count as free, or the cap
# stops capping.
STUB_COST_USD = float(os.environ.get("SOLVE_STUB_COST_USD", "0.02"))
DAY_TTL = 86_400
CACHE_TTL = 30 * DAY_TTL

# Status codes, one per gate. Documented here and in .env.example.
#   400 malformed request (no prompt) — before any gate, nothing spent
#   403 turnstile verification failed
#   200 cache hit (body.cached == true) or fresh generation
#   402 per-session/IP daily quota exhausted — body carries the BYO-key path
#   503 global monthly spend cap reached, free tier off — BYO key still works
#   429 upstream rate limit — not our bug, nothing charged
#   502 generation failed
#   401 admin endpoint, bad or missing shared secret


# --------------------------------------------------------------------------- #
# redaction
# --------------------------------------------------------------------------- #

# Every vendor prefix in use: sk- (OpenAI), nvapi- (NVIDIA), AIza (Google).
# A pattern that knows only one of them lets the others through, and a leaked
# key is equally bad whoever issued it.
_SK_RE = re.compile(r"(?:sk-|nvapi-|AIza)[A-Za-z0-9_-]{8,}")


def redact(text, secret=None):
    """Scrub anything key-shaped. `secret` scrubs a key that isn't `sk-` shaped."""
    out = _SK_RE.sub("[redacted-key]", str(text))
    if secret and len(str(secret)) >= 8:
        out = out.replace(str(secret), "[redacted-key]")
    return out


def log(msg, secret=None):
    """The only logger. Everything on the /api path goes through the redactor."""
    print("[leetviz]", redact(msg, secret), file=sys.stderr, flush=True)


# --------------------------------------------------------------------------- #
# KV — one module, one seam. Swap the class, not the callers.
# --------------------------------------------------------------------------- #


class _KV:
    """Vercel KV / Upstash Redis over its REST API. stdlib only."""

    def __init__(self, url, token):
        self.url = url.rstrip("/")
        self.token = token

    def _call(self, path, query="", body=None):
        req = urllib.request.Request(
            f"{self.url}/{path}{query}",
            data=body,
            headers={"Authorization": f"Bearer {self.token}"},
            method="POST" if body is not None else "GET",
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return json.load(r).get("result")
        except (urllib.error.URLError, ValueError, TimeoutError) as e:
            # A KV outage must not hand out free generations, but it also must
            # not hard-fail a read. Reads return None; writes are best-effort.
            log(f"KV error on {path.split('/')[0]}: {type(e).__name__}")
            return None

    @staticmethod
    def _q(s):
        return urllib.parse.quote(str(s), safe="")

    def get(self, key):
        return self._call(f"get/{self._q(key)}")

    def set(self, key, value, ttl=None):
        q = f"?EX={int(ttl)}" if ttl else ""
        self._call(f"set/{self._q(key)}", q, str(value).encode())

    def incr(self, key, by=1, ttl=None):
        cmd = "incrbyfloat" if isinstance(by, float) else "incrby"
        out = self._call(f"{cmd}/{self._q(key)}/{self._q(by)}")
        if ttl:
            self._call(f"expire/{self._q(key)}/{int(ttl)}/NX")
        return num(out)


class _FileKV:
    """Offline fallback so the gates are testable without KV credentials.

    Loud on construction and refused outright in production. Not a second
    storage backend to maintain — it is a dev shim with the same four methods.
    ponytail: read-modify-write with no lock; a real store is the upgrade path.
    """

    def __init__(self, path):
        self.path = Path(path)
        log(f"WARNING: no KV credentials — using file store at {self.path}. Dev only.")

    def _load(self):
        try:
            return json.loads(self.path.read_text())
        except (OSError, ValueError):
            return {}

    def _save(self, d):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(d))

    def get(self, key):
        row = self._load().get(key)
        if not row or (row[1] and row[1] < time.time()):
            return None
        return row[0]

    def set(self, key, value, ttl=None):
        d = self._load()
        d[key] = [str(value), time.time() + ttl if ttl else 0]
        self._save(d)

    def incr(self, key, by=1, ttl=None):
        d = self._load()
        row = d.get(key)
        cur = num(row[0]) if row and (not row[1] or row[1] >= time.time()) else 0
        exp = row[1] if row and row[1] else (time.time() + ttl if ttl else 0)
        d[key] = [str(cur + by), exp]
        self._save(d)
        return cur + by


def _make_store():
    url, token = os.environ.get("KV_REST_API_URL"), os.environ.get("KV_REST_API_TOKEN")
    if url and token:
        return _KV(url, token)
    if IS_PROD:
        raise RuntimeError("KV_REST_API_URL/TOKEN are required in production")
    return _FileKV(os.environ.get("KV_LOCAL_PATH", "/tmp/leetviz-kv.json"))


store = _make_store()


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


# --------------------------------------------------------------------------- #
# keys and clocks
# --------------------------------------------------------------------------- #


def _now():
    return datetime.now(timezone.utc)


def day_key(now=None):
    return (now or _now()).strftime("%Y-%m-%d")


def month_key(now=None):
    return (now or _now()).strftime("%Y-%m")


def month_resets(now=None):
    n = now or _now()
    return (n.replace(day=28) + timedelta(days=4)).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    ).isoformat()


def anon(s):
    """IPs are hashed before they reach KV — the quota needs an identity, not a PII record."""
    return hashlib.sha256(str(s).encode()).hexdigest()[:16]


def local_hash(prompt):
    """Whitespace-collapse + casefold, no model. Also the floor prompt_hash falls
    back to, so a trace stored under a local hash is found by either path."""
    return hashlib.sha256(" ".join(prompt.split()).casefold().encode()).hexdigest()[:16]


def prompt_hash(prompt):
    """Normalize + hash. OPENAI_MODEL_CHEAP canonicalises 'find the two indices
    that sum to k' onto the same cache key as 'Two Sum'; whitespace collapse +
    casefold is the floor it falls back to when the cheap model is unavailable.

    ponytail: an LLM in the cache key is only as stable as the model's output.
    Temperature is default and the answer is a short canonical title, which is
    stable in practice; a drift shows up as a cache miss, never as a wrong trace.
    """
    import _gen  # deferred: _gen imports this module

    return hashlib.sha256(
        " ".join((_gen.canonical(prompt) or prompt).split()).casefold().encode()
    ).hexdigest()[:16]


# --------------------------------------------------------------------------- #
# gates
# --------------------------------------------------------------------------- #


def verify_turnstile(token, ip):
    secret = os.environ.get("TURNSTILE_SECRET")
    if not secret:
        if IS_PROD:
            log("TURNSTILE_SECRET missing in production — failing closed")
            return False
        log("WARNING: TURNSTILE_SECRET unset — captcha gate disabled. Dev only.")
        return True
    if not token:
        return False
    data = urllib.parse.urlencode(
        {"secret": secret, "response": token, "remoteip": ip or ""}
    ).encode()
    try:
        with urllib.request.urlopen(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify", data, timeout=5
        ) as r:
            return bool(json.load(r).get("success"))
    except (urllib.error.URLError, ValueError, TimeoutError) as e:
        log(f"turnstile verify failed: {type(e).__name__}")
        return False


def generate(prompt, byo_key=None):
    """Returns (trace, cost_usd, usage). The work is in `_gen.generate`.

    `byo_key` is passed straight through as the API credential and is never
    stored, never logged and never echoed — the redaction path is real.
    """
    import _gen  # deferred: _gen imports this module

    return _gen.generate(prompt, byo_key)


def solve(prompt, turnstile_token, session_id, ip, byo_key=None):
    """The gate chain. Returns (status, body, audit).

    `audit` names every gate entered, in order. It never reaches the client.
    """
    audit = []
    m, d = month_key(), day_key()

    prompt = (prompt or "").strip()
    if not prompt:
        return 400, {"error": "prompt required"}, audit

    # 1. turnstile — cheapest possible rejection of a bot
    audit.append("turnstile")
    if not verify_turnstile(turnstile_token, ip):
        return 403, {"error": "captcha verification failed"}, audit

    # 2. normalize + hash
    audit.append("hash")
    # Byte-identical text can only land on the key it landed on last time, so
    # look that up before paying the cheap model to tell us the same thing. On
    # OpenAI nano the normalize call was ~1s; on a congested NIM free tier it is
    # 100s+, which made an already-stored answer as slow as generating it. This
    # short-circuits rather than reorders: a prompt that is NOT a byte-for-byte
    # repeat still goes through normalize before the cache, so the semantic
    # dedupe the ladder exists for is untouched.
    fast = local_hash(prompt)
    hit = store.get(f"cache:{fast}")
    h = fast if hit else prompt_hash(prompt)

    # 3. cache — a hit costs nothing, so it must not touch quota or spend
    audit.append("cache")
    cached = hit or store.get(f"cache:{h}")
    if cached:
        store.incr(f"stat:{m}:hit", 1)
        return 200, {"hash": h, "cached": True, "trace": json.loads(cached)}, audit

    # 4. per-session quota, counted against the cookie AND the IP
    audit.append("quota")
    qs, qi = f"quota:s:{session_id}:{d}", f"quota:i:{anon(ip)}:{d}"
    if not byo_key:
        used = max(num(store.get(qs)), num(store.get(qi)))
        if used >= FREE_PER_DAY:
            return (
                402,
                {
                    "error": "daily free limit reached",
                    "limit": FREE_PER_DAY,
                    "resets": "24h after your first generation today",
                    "byoKey": {
                        "header": "x-byo-key",
                        "how": "Add your own OpenAI key in the browser to keep going. "
                        "It stays in localStorage, is sent per request and is never stored.",
                    },
                },
                audit,
            )

    # 5. global monthly spend cap — the free tier switches off, BYO keeps working
    audit.append("cap")
    spent = num(store.get(f"spend:{m}"))
    if not byo_key and spent >= MONTHLY_CAP_USD:
        return (
            503,
            {
                "error": "monthly budget cap reached",
                "capUsd": MONTHLY_CAP_USD,
                "spentUsd": round(spent, 4),
                "resets": month_resets(),
                "byoKey": {
                    "header": "x-byo-key",
                    "how": "Free generations are off until the cap resets. Your own "
                    "OpenAI key still works and is never stored.",
                },
            },
            audit,
        )

    # 6. generate — the first expensive thing in this function
    audit.append("generate")
    try:
        trace, cost, usage = generate(prompt, byo_key)
    except Exception as e:  # noqa: BLE001 — the reason must not leak the key
        log(f"generation failed: {type(e).__name__}: {e}", byo_key)
        # "generation failed" is true of every branch here and useful in none.
        # A rate limit is the one a caller can act on, and it is not our bug,
        # so name it. The upstream text is never echoed — it can quote the key.
        if getattr(e, "code", None) == 429:
            # Same status, opposite advice: a rate limit clears by waiting, an
            # exhausted quota needs billing or a different provider. Telling
            # someone to "wait a minute" for the latter wastes their afternoon.
            reason = getattr(e, "api_code", "") or "rate_limit_exceeded"
            return 429, {"error": "rate-limited", "reason": reason}, audit
        return 502, {"error": "generation failed"}, audit

    # 7. record spend + decrement quota
    # ponytail: check-then-increment, so N concurrent requests from one session
    # can each pass gate 4. Upgrade path is an atomic INCR at the gate with a
    # refund when a later gate rejects; not worth it at 5/day.
    audit.append("record")
    ver = prompt_version()
    blob = json.dumps(trace)
    store.set(f"cache:{h}", blob, CACHE_TTL)
    # Also key it by the model-free hash of the exact text, so the fast path at
    # gate 2 can find it. Without this, a byte-identical repeat misses the cheap
    # lookup and pays the normalize call just to rediscover the same entry.
    if (fast := local_hash(prompt)) != h:
        store.set(f"cache:{fast}", blob, CACHE_TTL)
    store.set(f"promptver:{h}", ver, CACHE_TTL)  # trace a bad generation to its prompt
    store.incr(f"stat:{m}:{'byo' if byo_key else 'gen'}", 1)
    # Token counters are recorded for BYO too: they are usage, not spend.
    for name in ("prompt", "cached", "out_total", "out_visible", "reasoning", "calls"):
        if usage.get(name):
            store.incr(f"tok:{m}:{name}", int(usage[name]))
    if not byo_key:
        store.incr(qs, 1, DAY_TTL)
        store.incr(qi, 1, DAY_TTL)
        store.incr(f"spend:{m}", float(cost))
        store.incr(f"spend:{d}", float(cost), 40 * DAY_TTL)
    return 200, {"hash": h, "cached": False, "promptVersion": ver, "trace": trace}, audit


def prompt_version():
    import _gen  # deferred: _gen imports this module

    return _gen.prompt_version()


def spend_report():
    """Real counters, not estimates. Every number here is a KV read."""
    m, d = month_key(), day_key()
    month = num(store.get(f"spend:{m}"))
    gen = num(store.get(f"stat:{m}:gen"))
    hit = num(store.get(f"stat:{m}:hit"))
    byo = num(store.get(f"stat:{m}:byo"))
    served = hit + gen + byo
    tok = {k: num(store.get(f"tok:{m}:{k}")) for k in
           ("prompt", "cached", "out_total", "out_visible", "reasoning", "calls")}
    import _gen  # deferred: _gen imports this module

    return {
        "month": m,
        "spendTodayUsd": round(num(store.get(f"spend:{d}")), 4),
        "spendMonthUsd": round(month, 4),
        # The cheap normalize model runs on the hash gate, before the cache gate,
        # so it bills on cache hits too. Counted apart so a hit still costs the
        # generation budget nothing — see CLAUDE.md.
        "normalizeSpendMonthUsd": round(num(store.get(f"norm:{m}:usd")), 6),
        "capUsd": MONTHLY_CAP_USD,
        "headroomUsd": round(max(0.0, MONTHLY_CAP_USD - month), 4),
        "capReached": month >= MONTHLY_CAP_USD,
        "resets": month_resets(),
        "generations": int(gen),
        "byoGenerations": int(byo),
        "cacheHits": int(hit),
        # served = hits + generations; a request blocked by a gate never got served.
        "cacheHitRate": round(hit / served, 4) if served else None,
        "costPerGenerationUsd": round(month / gen, 6) if gen else None,
        "freePerDay": FREE_PER_DAY,
        "store": type(store).__name__,
        # --- token accounting. Reasoning tokens bill as output but never appear
        # in the response, so the visible count is NOT the billed count.
        "promptTokensMonth": int(tok["prompt"]),
        "cachedPromptTokensMonth": int(tok["cached"]),
        "promptCacheRate": round(tok["cached"] / tok["prompt"], 4) if tok["prompt"] else None,
        "outputTokensMonthBilled": int(tok["out_total"]),
        "outputTokensMonthVisible": int(tok["out_visible"]),
        "reasoningTokensMonth": int(tok["reasoning"]),
        "modelCallsMonth": int(tok["calls"]),
        "callsPerGeneration": round(tok["calls"] / (gen + byo), 3) if (gen + byo) else None,
        # --- which vendor served. A permanent OpenAI outage would otherwise show
        # only as "still working" while every trace quietly came from the fallback.
        "generationsByProvider": {
            p.id: int(num(store.get(f"prov:{m}:{p.id}")))
            for p in _gen._ALL.values()
        },
        "providerChain": [p.id for p in _gen.chain("GENERATE")] or None,
        # --- provenance: which prompt and which models are live right now
        "promptVersion": _gen.prompt_version(),
        "modelCheap": _gen.model("CHEAP") or "(unset — local canonicalisation)",
        "modelGenerate": _gen.model("GENERATE") or "(unset — offline dev generator)",
        "modelRepair": _gen.model("REPAIR") or "(unset)",
        "maxOutputTokens": _gen.MAX_OUTPUT_TOKENS,
    }


def admin_ok(header_value):
    secret = os.environ.get("ADMIN_SECRET")
    if not secret:
        return False  # unset means closed, never open
    return hmac.compare_digest(str(header_value or ""), secret)


# --------------------------------------------------------------------------- #
# HTTP shim — Vercel's Python runtime wants a BaseHTTPRequestHandler named
# `handler`; the three endpoints share everything except their verb bodies.
# --------------------------------------------------------------------------- #


class JSONHandler(BaseHTTPRequestHandler):
    SID = "lv_sid"

    def log_message(self, fmt, *args):  # the default logger writes to stderr unredacted
        log(fmt % args)

    def reply(self, status, body, cookie=None):
        raw = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        if cookie:
            self.send_header(
                "Set-Cookie",
                f"{self.SID}={cookie}; Path=/; Max-Age={DAY_TTL}; SameSite=Lax; HttpOnly; Secure",
            )
        self.end_headers()
        self.wfile.write(raw)

    def payload(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return {}

    def query(self, name):
        q = urllib.parse.urlparse(self.path).query
        return urllib.parse.parse_qs(q).get(name, [""])[0]

    def client_ip(self):
        fwd = self.headers.get("x-forwarded-for", "")
        return fwd.split(",")[0].strip() or self.client_address[0]

    def session(self):
        """Returns (sid, set_cookie_or_None)."""
        jar = SimpleCookie(self.headers.get("Cookie", ""))
        sid = jar[self.SID].value if self.SID in jar else None
        if sid and re.fullmatch(r"[0-9a-f]{32}", sid):
            return sid, None
        sid = secrets.token_hex(16)
        return sid, sid
