"use client";

import { useEffect, useMemo, useState } from "react";
import { stateAt, touched } from "@/lib/fold";
import type { Problem, Val } from "@/lib/schema";
import { ArrayView, MapView, ScalarView } from "./Renderers";

const TICK_MS = 700;

export default function Viewer({ problem }: { problem: Problem }) {
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

  const select = (nextAi: number, nextVi: number) => {
    setAi(nextAi);
    setVi(nextVi);
    setStep(0);
    setPlaying(false);
  };

  useEffect(() => {
    if (!playing) return;
    if (at >= last) return setPlaying(false);
    const id = setTimeout(() => setStep(at + 1), TICK_MS);
    return () => clearTimeout(id);
  }, [playing, at, last]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight") setStep((s) => Math.min(s + 1, last));
      else if (e.key === "ArrowLeft") setStep((s) => Math.max(s - 1, 0));
      else if (e.key === " ") setPlaying((p) => !p);
      else return;
      e.preventDefault();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [last]);

  // Pointer vars render inside the array they index, not as their own chip.
  const pointerOf: Record<string, string> = {};
  for (const [name, spec] of Object.entries(approach.viz)) {
    if (spec.startsWith("pointer:")) pointerOf[name] = spec.slice(8);
  }
  const pointers: Record<string, { name: string; index: number }[]> = {};
  for (const [name, arr] of Object.entries(pointerOf)) {
    const v = state[name];
    if (typeof v === "number") (pointers[arr] ??= []).push({ name, index: v });
  }

  // Map keys written this step, so the entry that just landed can flash.
  const changedKeys: Record<string, Set<string>> = {};
  for (const op of steps[at]?.ops ?? []) {
    const [root, key] = op[1];
    if (key !== undefined) (changedKeys[String(root)] ??= new Set()).add(String(key));
  }

  const scalars: [string, Val][] = [];
  const blocks = Object.entries(state).flatMap(([name, value]) => {
    if (name in pointerOf) return [];
    if (Array.isArray(value))
      return [
        <ArrayView
          key={name}
          name={name}
          value={value}
          pointers={pointers[name] ?? []}
          hit={hits.has(name)}
        />,
      ];
    if (value && typeof value === "object")
      return [
        <MapView
          key={name}
          name={name}
          value={value}
          changed={changedKeys[name] ?? new Set()}
          hit={hits.has(name)}
        />,
      ];
    scalars.push([name, value]);
    return [];
  });

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

        <div className="panel">
          <div className="viz">
            {blocks}
            <ScalarView entries={scalars} hits={hits} />
            {at === last && (
              <div className="result">return {JSON.stringify(variant.result)}</div>
            )}
          </div>
        </div>
      </div>

      <div className={steps[at].note ? "note" : "note empty"}>
        {steps[at].note ?? "…"}
      </div>

      <div className="player">
        <button onClick={() => setStep(0)} title="First step">
          ⏮
        </button>
        <button onClick={() => setStep(Math.max(at - 1, 0))} title="Back">
          ◀
        </button>
        <button onClick={() => setPlaying((p) => !p)} title="Play/pause">
          {playing ? "❚❚" : "▶"}
        </button>
        <button onClick={() => setStep(Math.min(at + 1, last))} title="Forward">
          ▶
        </button>
        <button onClick={() => setStep(last)} title="Last step">
          ⏭
        </button>
        <input
          type="range"
          min={0}
          max={last}
          value={at}
          onChange={(e) => {
            setPlaying(false);
            setStep(Number(e.target.value));
          }}
        />
        <span className="count">
          {at + 1} / {last + 1}
        </span>
      </div>
      <p className="hint">← → to step, space to play. Scrubbing works in both directions.</p>
    </>
  );
}
