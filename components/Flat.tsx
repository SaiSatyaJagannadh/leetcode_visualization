import type { Val } from "@/lib/schema";

/** Renderers for the flat kinds: array, stack, queue, bits, grid, intervals, map. */

export function show(v: Val): string {
  if (v === null) return "null";
  if (typeof v === "string") return v;
  if (typeof v === "object") return JSON.stringify(v);
  return String(v);
}

export type Marker = { name: string; index: number };

export function CellsView({
  name,
  value,
  markers = [],
  kind,
  hit,
}: {
  name: string;
  value: Val[];
  markers?: Marker[];
  kind: "array" | "stack" | "queue" | "bits";
  hit: boolean;
}) {
  // A stack grows at its end, so the end is what gets labelled.
  const ends: Record<number, string> = {};
  if (value.length) {
    if (kind === "stack") ends[value.length - 1] = "top";
    if (kind === "queue") {
      ends[0] = "front";
      if (value.length > 1) ends[value.length - 1] = "back";
    }
  }
  return (
    <div className={hit ? "var hit" : "var"}>
      <span className="name">
        {name}
        {kind !== "array" && <em> {kind}</em>}
      </span>
      {value.length === 0 ? (
        <span className="empty-note">empty</span>
      ) : (
        <div className={kind === "bits" ? "cells tight" : "cells"}>
          {value.map((v, i) => {
            const on = markers.filter((m) => m.index === i);
            return (
              <div className={on.length ? "cell hit" : "cell"} key={i}>
                <span className="box">{show(v)}</span>
                <span className="idx">{ends[i] ?? i}</span>
                <span className="ptrs">{on.map((m) => m.name).join(" ")}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export function GridView({
  name,
  value,
  row,
  col,
  cells,
  hit,
}: {
  name: string;
  value: Val[][];
  row?: number;
  col?: number;
  cells?: number[][];
  hit: boolean;
}) {
  const front = new Set((cells ?? []).map(([r, c]) => `${r},${c}`));
  return (
    <div className={hit ? "var hit" : "var"}>
      <span className="name">{name}</span>
      <div className="grid">
        {value.map((r, ri) => (
          <div className="grow" key={ri}>
            {(Array.isArray(r) ? r : []).map((v, ci) => {
              const cls = [
                "gcell",
                ri === row && ci === col && "hit",
                front.has(`${ri},${ci}`) && "front",
                v === 0 && "zero",
              ]
                .filter(Boolean)
                .join(" ");
              return (
                <span className={cls} key={ci}>
                  {show(v)}
                </span>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}

export function IntervalsView({
  name,
  value,
  hit,
  scale,
}: {
  name: string;
  value: Val[];
  hit: boolean;
  scale: [number, number];
}) {
  const [lo, hi] = scale;
  const span = hi - lo || 1;
  const rows = (Array.isArray(value[0]) ? value : [value]) as number[][];
  return (
    <div className={hit ? "var hit" : "var"}>
      <span className="name">{name}</span>
      {!rows.length ? (
        <span className="empty-note">empty</span>
      ) : (
        <div className="spans">
          {rows.map(([a, b], i) => (
            <div className="span-row" key={i}>
              <span
                className="bar"
                style={{
                  marginLeft: `${((a - lo) / span) * 100}%`,
                  width: `${Math.max(((b - a) / span) * 100, 1.5)}%`,
                }}
              >
                {a}–{b}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export function MapView({
  name,
  value,
  changed,
  hit,
}: {
  name: string;
  value: Record<string, Val>;
  changed: Set<string>;
  hit: boolean;
}) {
  const entries = Object.entries(value);
  return (
    <div className={hit ? "var hit" : "var"}>
      <span className="name">{name}</span>
      {entries.length === 0 ? (
        <span className="empty-note">empty</span>
      ) : (
        <div className="kv">
          {entries.map(([k, v]) => (
            <span className={changed.has(k) ? "pair hit" : "pair"} key={k}>
              <span className="k">{k}</span> → {show(v)}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

export function ScalarView({ entries, hits }: { entries: [string, Val][]; hits: Set<string> }) {
  if (!entries.length) return null;
  return (
    <div className="var">
      <div className="scalars">
        {entries.map(([k, v]) => (
          <span className={hits.has(k) ? "chip hit" : "chip"} key={k}>
            <span className="k">{k} = </span>
            {show(v)}
          </span>
        ))}
      </div>
    </div>
  );
}
