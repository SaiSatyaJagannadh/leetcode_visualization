import type { Val } from "@/lib/schema";
import { show } from "./Flat";

/**
 * One SVG for every node-shaped kind. Linked lists, trees, graphs, call trees
 * and tries all reduce to nodes with coordinates plus directed edges, so they
 * share this and differ only in the adapter that feeds it.
 */

export type DNode = {
  id: string;
  x: number;
  y: number;
  label: string;
  sub?: string;
  hot?: boolean;
  dim?: boolean;
  marks?: string[];
};
export type DEdge = { from: string; to: string; label?: string; hot?: boolean };

const R = 19;
const GAP_X = 74;
const GAP_Y = 76;
const PAD = 30;

export function Diagram({
  nodes,
  edges,
  onPick,
}: {
  nodes: DNode[];
  edges: DEdge[];
  onPick?: (id: string) => void;
}) {
  if (!nodes.length) return <span className="empty-note">empty</span>;

  const xs = nodes.map((n) => n.x);
  const ys = nodes.map((n) => n.y);
  const spanX = Math.max(...xs) - Math.min(...xs) || 1;
  const spanY = Math.max(...ys) - Math.min(...ys);
  const minX = Math.min(...xs);
  const minY = Math.min(...ys);

  const px = (n: DNode) => PAD + ((n.x - minX) / spanX) * (spanX * GAP_X);
  const py = (n: DNode) => PAD + (n.y - minY) * GAP_Y;
  const at = new Map(nodes.map((n) => [n.id, { x: px(n), y: py(n) }]));

  const w = PAD * 2 + spanX * GAP_X;
  // Arcs bow below the row they connect, so reserve room or they get clipped.
  const arcs = edges.some((e) => {
    const a = at.get(e.from);
    const b = at.get(e.to);
    return a && b && e.from !== e.to && a.y === b.y && Math.abs(b.x - a.x) > GAP_X * 1.4;
  });
  const h = PAD * 2 + spanY * GAP_Y + (arcs ? R + 60 : 0);

  return (
    <svg className="diagram" viewBox={`0 0 ${w} ${h}`} style={{ maxHeight: h + 10 }}>
      <defs>
        <marker id="ah" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
          <path d="M0,0 L8,4 L0,8 z" fill="#5b6775" />
        </marker>
        <marker id="ah-hot" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">
          <path d="M0,0 L8,4 L0,8 z" fill="#f0883e" />
        </marker>
      </defs>

      {edges.map((e, i) => {
        const a = at.get(e.from);
        const b = at.get(e.to);
        if (!a || !b) return null;
        // Stop the line at the rim so the arrowhead isn't buried in the circle.
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const len = Math.hypot(dx, dy) || 1;
        const self = e.from === e.to;
        const x2 = b.x - (dx / len) * (R + 8);
        const y2 = b.y - (dy / len) * (R + 8);
        // A long edge along one row would lie on top of the nodes between it —
        // a list's cycle edge is exactly this case. Arc it clear instead.
        const arc = !self && a.y === b.y && Math.abs(dx) > GAP_X * 1.4;
        const lift = (dx < 0 ? 1 : -1) * (R + 24);
        return (
          <g key={i}>
            {self ? (
              <path
                className={e.hot ? "edge hot" : "edge"}
                d={`M${a.x - 8},${a.y - R} a 16,16 0 1,1 16,0`}
                markerEnd={e.hot ? "url(#ah-hot)" : "url(#ah)"}
                fill="none"
              />
            ) : arc ? (
              <path
                className={e.hot ? "edge hot" : "edge"}
                d={`M${a.x},${a.y + Math.sign(lift) * R} Q${(a.x + b.x) / 2},${
                  a.y + lift * 2
                } ${b.x},${b.y + Math.sign(lift) * R}`}
                markerEnd={e.hot ? "url(#ah-hot)" : "url(#ah)"}
                fill="none"
              />
            ) : (
              <line
                className={e.hot ? "edge hot" : "edge"}
                x1={a.x + (dx / len) * R}
                y1={a.y + (dy / len) * R}
                x2={x2}
                y2={y2}
                markerEnd={e.hot ? "url(#ah-hot)" : "url(#ah)"}
              />
            )}
            {e.label && (
              <text className="edge-label" x={(a.x + b.x) / 2} y={(a.y + b.y) / 2 - 5}>
                {e.label}
              </text>
            )}
          </g>
        );
      })}

      {nodes.map((n) => {
        const p = at.get(n.id)!;
        const cls = ["node", n.hot && "hot", n.dim && "dim", onPick && "pick"]
          .filter(Boolean)
          .join(" ");
        return (
          <g key={n.id} className={cls} onClick={onPick && (() => onPick(n.id))}>
            <circle cx={p.x} cy={p.y} r={R} />
            <text className="node-label" x={p.x} y={p.y + 4}>
              {n.label}
            </text>
            {n.sub && (
              <text className="node-sub" x={p.x} y={p.y + R + 13}>
                {n.sub}
              </text>
            )}
            {n.marks?.length ? (
              <text className="node-mark" x={p.x} y={p.y - R - 7}>
                {n.marks.join(" ")}
              </text>
            ) : null}
          </g>
        );
      })}
    </svg>
  );
}

/* --- adapters ---------------------------------------------------------- */

type Nodes = Record<string, Record<string, Val>>;

const ref = (v: Val): string | null =>
  v && typeof v === "object" && !Array.isArray(v) && "$ref" in v ? String(v.$ref) : null;

/** Linked lists and trees: coordinates were baked in Python. */
export function fromNodes(nodes: Nodes, marks: Record<string, string[]>, hot: Set<string>) {
  const dn: DNode[] = [];
  const de: DEdge[] = [];
  for (const [id, n] of Object.entries(nodes)) {
    const at = (n.at ?? [0, 0]) as number[];
    dn.push({
      id,
      x: at[0],
      y: at[1],
      label: String(n.val ?? ""),
      hot: hot.has(id),
      marks: marks[id],
    });
    for (const side of ["next", "left", "right", "random"]) {
      const to = ref(n[side]);
      if (to)
        de.push({
          from: id,
          to,
          label: side === "next" ? undefined : side === "random" ? "rand" : side[0],
          hot: hot.has(id),
        });
    }
  }
  return { nodes: dn, edges: de };
}

/** Recursion: x is call order, y is depth, both baked at trace time. */
export function fromCalls(calls: Nodes, activeId: string | null) {
  const dn: DNode[] = [];
  const de: DEdge[] = [];
  for (const [id, c] of Object.entries(calls)) {
    const at = (c.at ?? [0, 0]) as number[];
    const args = Object.entries((c.args ?? {}) as Record<string, Val>)
      .map(([k, v]) => `${k}=${show(v)}`)
      .join(" ");
    const returned = c.status === "returned";
    // A leaf that came back with nothing is a dead branch, not a real answer.
    const pruned = returned && !Object.values(calls).some((o) => o.parent === id) && !c.ret;
    dn.push({
      id,
      x: at[0],
      y: at[1],
      label: String(c.ret ?? "…"),
      sub: args,
      hot: id === activeId,
      dim: pruned,
      marks: pruned ? ["✕"] : undefined,
    });
    if (c.parent != null) de.push({ from: String(c.parent), to: id, hot: id === activeId });
  }
  return { nodes: dn, edges: de };
}

/** Graphs: adjacency dict plus the circular layout baked per approach. */
export function fromGraph(
  adj: Record<string, Val>,
  layout: Record<string, [number, number]>,
  labels: Record<string, Val>,
  marked: Set<string>
) {
  const dn: DNode[] = Object.keys(adj).map((k) => ({
    id: k,
    x: layout[k]?.[0] ?? 0,
    y: layout[k]?.[1] ?? 0,
    label: k,
    sub: labels[k] !== undefined ? String(labels[k]) : undefined,
    hot: marked.has(k),
  }));
  const de: DEdge[] = [];
  for (const [from, out] of Object.entries(adj)) {
    for (const e of Array.isArray(out) ? out : []) {
      const [to, w] = Array.isArray(e) ? e : [e, undefined];
      de.push({ from, to: String(to), label: w === undefined ? undefined : String(w) });
    }
  }
  return { nodes: dn, edges: de };
}

/** A heap is a complete tree, so index arithmetic *is* the layout. */
export function fromHeap(arr: Val[]) {
  const depth = (i: number) => Math.floor(Math.log2(i + 1));
  const maxD = depth(Math.max(arr.length - 1, 0));
  const dn: DNode[] = arr.map((v, i) => {
    const d = depth(i);
    const within = i - (2 ** d - 1);
    return {
      id: String(i),
      // Spread each level across the same width so parents sit above their children.
      x: (within + 0.5) * 2 ** (maxD - d),
      y: d,
      label: show(v),
      sub: String(i),
    };
  });
  const de: DEdge[] = arr
    .map((_, i) => i)
    .filter((i) => i > 0)
    .map((i) => ({ from: String((i - 1) >> 1), to: String(i) }));
  return { nodes: dn, edges: de };
}

/** Tries are nested dicts that reshape every step, so they lay out here. */
export function fromTrie(root: Record<string, Val>) {
  const dn: DNode[] = [{ id: "", x: 0, y: 0, label: "•" }];
  const de: DEdge[] = [];
  let leaf = 0;
  const walk = (node: Record<string, Val>, path: string, depth: number): number => {
    const kids = Object.entries(node);
    if (!kids.length) return leaf++;
    const centres = kids.map(([ch, child]) => {
      const id = path + ch;
      const x = walk(child as Record<string, Val>, id, depth + 1);
      dn.push({ id, x, y: depth + 1, label: ch === "$" ? "■" : ch, dim: ch === "$" });
      de.push({ from: path, to: id });
      return x;
    });
    return centres.reduce((a, b) => a + b, 0) / centres.length;
  };
  dn[0].x = walk(root, "", 0);
  return { nodes: dn, edges: de };
}
