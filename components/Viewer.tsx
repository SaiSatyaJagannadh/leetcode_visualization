"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { stateAt, touched } from "@/lib/fold";
import type { Problem } from "@/lib/schema";
import { Stage } from "./Stage";

const TICK_MS = 650;

/** `keys` is off in the gallery: eight viewers on one page would all step at once. */
export default function Viewer({ problem, keys = true }: { problem: Problem; keys?: boolean }) {
  const [ai, setAi] = useState(0);
  const [vi, setVi] = useState(0);
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(false);

  const approach = problem.approaches[ai];
  const variant = approach.variants[vi] ?? approach.variants[0];
  const steps = variant.steps;
  const last = steps.length - 1;
  const at = Math.min(step, last);

  const state = useMemo(() => stateAt(steps, at), [steps, at]);
  const hits = useMemo(() => touched(steps[at]), [steps, at]);

  const changed = useMemo(() => {
    const out: Record<string, Set<string>> = {};
    for (const op of steps[at]?.ops ?? []) {
      const [root, key] = op[1];
      if (key !== undefined) (out[String(root)] ??= new Set()).add(String(key));
    }
    return out;
  }, [steps, at]);

  const select = (nextAi: number, nextVi: number) => {
    setAi(nextAi);
    setVi(nextVi);
    setStep(0);
    setPlaying(false);
  };

  const jump = useCallback(
    (s: number) => {
      setPlaying(false);
      setStep(Math.max(0, Math.min(s, last)));
    },
    [last]
  );

  useEffect(() => {
    if (!playing) return;
    if (at >= last) return setPlaying(false);
    const id = setTimeout(() => setStep(at + 1), TICK_MS);
    return () => clearTimeout(id);
  }, [playing, at, last]);

  useEffect(() => {
    if (!keys) return;
    const onKey = (e: KeyboardEvent) => {
      // The shortcuts are on window, so without this space would toggle play
      // instead of pressing whichever tab or player button has focus, and the
      // slider's own arrow keys would never reach it.
      const el = e.target as HTMLElement | null;
      if (el?.closest("button, a, input, textarea, select, [contenteditable]")) return;
      if (e.key === "ArrowRight") setStep((s) => Math.min(s + 1, last));
      else if (e.key === "ArrowLeft") setStep((s) => Math.max(s - 1, 0));
      else if (e.key === " ") setPlaying((p) => !p);
      else return;
      e.preventDefault();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [keys, last]);

  return (
    <>
      <div className="tabs">
        {problem.approaches.map((a, i) => (
          <button key={a.id} aria-pressed={i === ai} onClick={() => select(i, 0)}>
            {a.label}
          </button>
        ))}
        <span className="cx">
          time {approach.complexity.time} · space {approach.complexity.space}
        </span>
      </div>

      <div className="tabs subtabs">
        {approach.variants.map((v, i) => (
          <button key={v.id} aria-pressed={i === vi} onClick={() => select(ai, i)}>
            {v.label}
          </button>
        ))}
      </div>

      <div className="stage">
        <div className="panel">
          <pre className="code">
            {approach.source.map((line, i) => (
              <span className={i === steps[at].line ? "ln on" : "ln"} key={i}>
                {line || " "}
              </span>
            ))}
          </pre>
        </div>

        <div className="panel scrollable">
          <Stage
            approach={approach}
            state={state}
            hits={hits}
            changed={changed}
            onJump={jump}
          />
          {at === last && (
            <div className="result">return {JSON.stringify(variant.result)}</div>
          )}
        </div>
      </div>

      {/* The note is the teaching content, so it has to be announced as the
          player advances rather than changing silently. */}
      <div className={steps[at].note ? "note" : "note empty"} aria-live="polite">
        {steps[at].note ?? "…"}
      </div>

      <div className="player">
        <button onClick={() => jump(0)} aria-label="First step" title="First step">
          ⏮
        </button>
        <button onClick={() => jump(at - 1)} aria-label="Previous step" title="Back">
          ◀
        </button>
        <button
          onClick={() => setPlaying((p) => !p)}
          aria-label={playing ? "Pause" : "Play"}
          title={playing ? "Pause" : "Play"}
        >
          {playing ? "❚❚" : "▶"}
        </button>
        <button onClick={() => jump(at + 1)} aria-label="Next step" title="Forward">
          ▶
        </button>
        <button onClick={() => jump(last)} aria-label="Last step" title="Last step">
          ⏭
        </button>
        <input
          type="range"
          min={0}
          max={last}
          value={at}
          aria-label="Step"
          aria-valuetext={`Step ${at + 1} of ${last + 1}`}
          onChange={(e) => jump(Number(e.target.value))}
        />
        <span className="count">
          {at + 1} / {last + 1}
        </span>
      </div>
      <p className="hint">← → to step, space to play. Scrubbing works in both directions.</p>
    </>
  );
}
