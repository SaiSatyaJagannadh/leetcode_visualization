"use client";

/**
 * The /solve, /s/[hash] and /admin/spend UIs. Not a player and not a renderer —
 * all three hand their trace to the one Viewer.
 */

import Script from "next/script";
import { useCallback, useEffect, useState } from "react";
import Viewer from "@/components/Viewer";
import { Problem } from "@/lib/schema";

const BYO_STORE = "leetviz.byoKey"; // the key lives here and nowhere else
const SITE_KEY = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY;

type Fail = { error: string; capUsd?: number; spentUsd?: number; resets?: string; limit?: number };

function useTrace() {
  const [trace, setTrace] = useState<Problem | null>(null);
  const [fail, setFail] = useState<Fail | null>(null);
  const [busy, setBusy] = useState(false);
  return { trace, setTrace, fail, setFail, busy, setBusy };
}

/**
 * The gate chain from api/_lib.solve(), in the order it actually runs. The
 * server returns which of these it entered, so this reports rather than mimes:
 * a cache hit visibly stops at `cache`, having cost nothing.
 */
const GATES = ["turnstile", "hash", "cache", "quota", "cap", "generate", "record"];

function Gates({ ran, busy, secs }: { ran: string[] | null; busy: boolean; secs: number }) {
  if (!ran && !busy) return null;
  // While the request is open we have no audit yet. Everything before
  // `generate` is sub-millisecond, so once we're a second in, those gates
  // provably passed — a failure would already have come back.
  const live = busy && secs >= 1;
  return (
    <ol className="gates" aria-label="Request pipeline">
      {GATES.map((g) => {
        const done = ran ? ran.includes(g) : live && GATES.indexOf(g) < GATES.indexOf("generate");
        const now = !ran && live && g === "generate";
        return (
          <li key={g} className={`gate${done ? " cleared" : ""}${now ? " live" : ""}`}>
            {g}
            {now && <span className="secs">{secs}s</span>}
          </li>
        );
      })}
    </ol>
  );
}

/** Honest copy per status. A 503 is the spend cap, not "try again later". */
function Problem_({ status, fail }: { status: number; fail: Fail }) {
  if (status === 402)
    return (
      <p className="note">
        You&apos;ve used your {fail.limit} free generations for today. They come back 24
        hours after the first one. To keep going now, paste your own OpenAI key below —
        it stays in this browser, is sent only with your own requests, and is never
        stored on the server.
      </p>
    );
  if (status === 503)
    return (
      <p className="note">
        LeetViz hit its ${fail.capUsd} monthly generation budget (${fail.spentUsd} spent),
        so free generations are off until{" "}
        {fail.resets ? new Date(fail.resets).toUTCString() : "the 1st"}. Nothing is broken
        — the meter ran out. Your own OpenAI key still works below.
      </p>
    );
  if (status === 403) return <p className="note">Captcha check failed. Reload and try again.</p>;
  if (status === 429)
    return (
      <p className="note">
        OpenAI is rate-limiting this key. Nothing was charged and your daily
        allowance is untouched. Wait a minute and trace it again, or use your own key below.
      </p>
    );
  return <p className="note">{fail.error}</p>;
}

export function SolveForm() {
  const { trace, setTrace, fail, setFail, busy, setBusy } = useTrace();
  const [status, setStatus] = useState(0);
  const [prompt, setPrompt] = useState("");
  const [hash, setHash] = useState("");
  const [byo, setByo] = useState("");
  const [token, setToken] = useState("");
  const [gates, setGates] = useState<string[] | null>(null);
  const [secs, setSecs] = useState(0);

  useEffect(() => setByo(localStorage.getItem(BYO_STORE) ?? ""), []);
  useEffect(() => {
    (window as unknown as { lvToken: (t: string) => void }).lvToken = setToken;
  }, []);

  const saveByo = (v: string) => {
    setByo(v);
    v ? localStorage.setItem(BYO_STORE, v) : localStorage.removeItem(BYO_STORE);
  };

  const submit = useCallback(async () => {
    setBusy(true);
    setFail(null);
    setTrace(null);
    setGates(null);
    const res = await fetch("/api/solve", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...(byo ? { "x-byo-key": byo } : {}) },
      body: JSON.stringify({ prompt, turnstileToken: token }),
    });
    const body = await res.json();
    setStatus(res.status);
    setGates(body.gates ?? null);
    if (res.ok) {
      setHash(body.hash);
      setTrace(Problem.parse(body.trace));
    } else setFail(body);
    setBusy(false);
  }, [prompt, byo, token, setBusy, setFail, setTrace]);

  // A generation runs ~45s. Without a moving number the page reads as hung,
  // which is exactly how this looked before.
  useEffect(() => {
    if (!busy) return setSecs(0);
    const t = setInterval(() => setSecs((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, [busy]);

  return (
    <>
      {SITE_KEY && (
        <Script src="https://challenges.cloudflare.com/turnstile/v0/api.js" defer />
      )}
      {/* Not `.prompt` — that class styles the problem statement paragraph on
          /p/[slug], and reusing it here left the textarea with browser defaults. */}
      <textarea
        className="ask"
        rows={6}
        placeholder="Paste a problem statement. Constraints and worked examples make the trace better."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />
      {SITE_KEY && (
        <div className="cf-turnstile" data-sitekey={SITE_KEY} data-callback="lvToken" />
      )}
      <p className="meta">
        <button className="tag link" onClick={submit} disabled={busy || !prompt.trim()}>
          {busy ? "tracing…" : "trace it"}
        </button>
        {hash && (
          <a className="tag link" href={`/s/${hash}`}>
            share link ↗
          </a>
        )}
      </p>
      <Gates ran={gates} busy={busy} secs={secs} />

      {fail && (
        <>
          <Problem_ status={status} fail={fail} />
          <p className="meta">
            <input
              className="tag"
              type="password"
              placeholder="sk-… your own OpenAI key"
              value={byo}
              onChange={(e) => saveByo(e.target.value)}
            />
          </p>
        </>
      )}
      {trace && <Viewer problem={trace} />}
    </>
  );
}

export function SharedTrace({ hash }: { hash: string }) {
  const { trace, setTrace, fail, setFail } = useTrace();
  useEffect(() => {
    fetch(`/api/share?h=${encodeURIComponent(hash)}`)
      .then((r) => r.json().then((b) => (r.ok ? setTrace(Problem.parse(b.trace)) : setFail(b))))
      .catch(() => setFail({ error: "could not load that link" }));
  }, [hash, setTrace, setFail]);
  if (fail) return <p className="note">{fail.error}</p>;
  if (!trace) return <p className="note">loading…</p>;
  return <Viewer problem={trace} />;
}

type Report = Record<string, string | number | boolean | null>;

export function SpendDash() {
  const [secret, setSecret] = useState("");
  const [rows, setRows] = useState<Report | null>(null);
  const [err, setErr] = useState("");

  const load = async () => {
    const res = await fetch("/api/admin/spend", { headers: { "x-admin-secret": secret } });
    const body = await res.json();
    res.ok ? (setRows(body), setErr("")) : setErr(body.error ?? "failed");
  };

  return (
    <>
      <p className="meta">
        <input
          className="tag"
          type="password"
          placeholder="admin secret"
          value={secret}
          onChange={(e) => setSecret(e.target.value)}
        />
        <button className="tag link" onClick={load}>
          load
        </button>
      </p>
      {err && <p className="note">{err}</p>}
      {rows && (
        <div className="kv">
          {Object.entries(rows).map(([k, v]) => (
            <div className="var" key={k}>
              <span className="lbl">{k}</span> <span>{v === null ? "—" : String(v)}</span>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
