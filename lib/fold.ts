import type { Op, Step, Val } from "./schema";

type State = Record<string, Val>;

function apply(state: State, op: Op) {
  const path = op[1];
  let node: any = state;
  for (const key of path.slice(0, -1)) node = node[key];
  const last = path[path.length - 1];
  if (op[0] === "del") delete node[last];
  else node[last] = structuredClone(op[2]);
}

/**
 * State after `index` steps. Replays from 0 every time — a few thousand ops is
 * nothing, and it means scrubbing backwards needs no inverse ops or snapshots.
 */
export function stateAt(steps: Step[], index: number): State {
  const state: State = {};
  for (let i = 0; i <= index && i < steps.length; i++) {
    for (const op of steps[i].ops) apply(state, op);
  }
  return state;
}

/** Root variable names touched by this step, for highlighting what just changed. */
export function touched(step: Step | undefined): Set<string> {
  return new Set(step?.ops.map((op) => String(op[1][0])) ?? []);
}
