import type { Approach, Val } from "@/lib/schema";
import { CellsView, GridView, IntervalsView, MapView, ScalarView, show } from "./Flat";
import { Diagram, fromCalls, fromGraph, fromHeap, fromNodes, fromTrie } from "./Diagram";

type State = Record<string, Val>;

/** Split "kind:target" into its parts. */
const spec = (s: string) => {
  const i = s.indexOf(":");
  return i < 0 ? ([s, ""] as const) : ([s.slice(0, i), s.slice(i + 1)] as const);
};

const asRef = (v: Val): string | null =>
  v && typeof v === "object" && !Array.isArray(v) && "$ref" in v ? String(v.$ref) : null;

const asRows = (v: Val): Val[][] => (Array.isArray(v) ? (v.filter(Array.isArray) as Val[][]) : []);

export function Stage({
  approach,
  state,
  hits,
  changed,
  onJump,
}: {
  approach: Approach;
  state: State;
  hits: Set<string>;
  changed: Record<string, Set<string>>;
  onJump: (step: number) => void;
}) {
  const viz = approach.viz;

  // Vars that decorate another var render inside it, not on their own.
  const attached: Record<string, { role: string; host: string; name: string }[]> = {};
  const consumed = new Set<string>();
  for (const [name, raw] of Object.entries(viz)) {
    const [role, host] = spec(raw);
    if (host) {
      (attached[host] ??= []).push({ role, host, name });
      consumed.add(name);
    }
    if (role === "node") consumed.add(name);
  }
  const kindOf = (name: string) => spec(viz[name] ?? "")[0];
  const aux = (host: string, role: string) =>
    (attached[host] ?? []).filter((a) => a.role === role);

  // Node pointers (head, prev, tail) become labels above the node they sit on.
  const nodeMarks: Record<string, string[]> = {};
  const hotNodes = new Set<string>();
  for (const [name, raw] of Object.entries(viz)) {
    if (spec(raw)[0] !== "node") continue;
    const id = asRef(state[name]);
    if (id) {
      (nodeMarks[id] ??= []).push(name);
      if (hits.has(name)) hotNodes.add(id);
    }
  }

  // Every interval var shares one horizontal scale, or the bars lie to you.
  const bounds = Object.entries(state)
    .filter(([n]) => kindOf(n).startsWith("interval"))
    .flatMap(([, v]) => asRows(v).flat() as number[]);
  const scale: [number, number] = bounds.length
    ? [Math.min(...bounds), Math.max(...bounds)]
    : [0, 1];

  const blocks: React.ReactNode[] = [];
  const scalars: [string, Val][] = [];

  // The object graph and the call tree lead, since they're the whole picture.
  const nodes = state.$nodes as Record<string, Record<string, Val>> | undefined;
  if (nodes && Object.keys(nodes).length) {
    const d = fromNodes(nodes, nodeMarks, hotNodes);
    blocks.push(
      <div className="var" key="$nodes">
        <span className="name">structure</span>
        <Diagram {...d} />
      </div>
    );
  }

  const calls = state.$calls as Record<string, Record<string, Val>> | undefined;
  if (calls && Object.keys(calls).length) {
    const active =
      Object.entries(calls)
        .filter(([, c]) => c.status === "active")
        .sort((a, b) => Number(b[1].depth) - Number(a[1].depth))[0]?.[0] ?? null;
    const d = fromCalls(calls, active);
    blocks.push(
      <div className="var" key="$calls">
        <span className="name">call tree — click a frame to jump to it</span>
        <Diagram
          {...d}
          onPick={(id) => onJump(Number(calls[id]?.enteredAt ?? 0))}
        />
      </div>
    );
  }

  for (const [name, value] of Object.entries(state)) {
    if (name.startsWith("$") || consumed.has(name)) continue;
    const kind = kindOf(name);
    const hit = hits.has(name);
    const markers = aux(name, "pointer")
      .map((a) => ({ name: a.name, index: Number(state[a.name]) }))
      .filter((m) => Number.isInteger(m.index));

    if (kind === "grid" || (!kind && asRows(value).length && Array.isArray(value))) {
      const rowVar = aux(name, "row")[0];
      const colVar = aux(name, "col")[0];
      const cellVar = aux(name, "cells")[0];
      blocks.push(
        <GridView
          key={name}
          name={name}
          value={asRows(value)}
          row={rowVar ? Number(state[rowVar.name]) : undefined}
          col={colVar ? Number(state[colVar.name]) : undefined}
          cells={cellVar ? (asRows(state[cellVar.name]) as number[][]) : undefined}
          hit={hit}
        />
      );
      continue;
    }

    if (kind === "graph") {
      const labelVar = aux(name, "labels")[0];
      const markVar = aux(name, "marked")[0];
      const marked = new Set(
        (Array.isArray(state[markVar?.name ?? ""]) ? (state[markVar.name] as Val[]) : []).map(String)
      );
      blocks.push(
        <div className="var" key={name}>
          <span className="name">{name}</span>
          <Diagram
            {...fromGraph(
              value as Record<string, Val>,
              (approach.layout[name] ?? {}) as Record<string, [number, number]>,
              (labelVar ? (state[labelVar.name] as Record<string, Val>) : {}) ?? {},
              marked
            )}
          />
        </div>
      );
      continue;
    }

    if (kind === "trie") {
      blocks.push(
        <div className="var" key={name}>
          <span className="name">{name}</span>
          <Diagram {...fromTrie((value ?? {}) as Record<string, Val>)} />
        </div>
      );
      continue;
    }

    if (kind === "heap" && Array.isArray(value)) {
      blocks.push(
        <div className="var" key={name}>
          <CellsView name={name} value={value} markers={markers} kind="array" hit={hit} />
          <Diagram {...fromHeap(value)} />
        </div>
      );
      continue;
    }

    if (kind.startsWith("interval")) {
      blocks.push(
        <IntervalsView key={name} name={name} value={value as Val[]} hit={hit} scale={scale} />
      );
      continue;
    }

    if (Array.isArray(value)) {
      const k = kind === "stack" || kind === "queue" || kind === "bits" ? kind : "array";
      blocks.push(
        <CellsView key={name} name={name} value={value} markers={markers} kind={k} hit={hit} />
      );
      continue;
    }

    if (value && typeof value === "object") {
      blocks.push(
        <MapView
          key={name}
          name={name}
          value={value as Record<string, Val>}
          changed={changed[name] ?? new Set()}
          hit={hit}
        />
      );
      continue;
    }

    scalars.push([name, value]);
  }

  return (
    <div className="viz">
      {blocks}
      <ScalarView entries={scalars} hits={hits} />
    </div>
  );
}

export { show };
