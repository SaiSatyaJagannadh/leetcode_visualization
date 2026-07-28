import { z } from "zod";

export const SCHEMA_VERSION = 1;

/** A value the tracer could serialise: JSON minus objects it couldn't reach. */
export type Val = string | number | boolean | null | Val[] | { [k: string]: Val };
const Val: z.ZodType<Val> = z.lazy(() =>
  z.union([z.string(), z.number(), z.boolean(), z.null(), z.array(Val), z.record(Val)])
);

const Path = z.array(z.union([z.string(), z.number()]));

/** Ops fold forward into the state object. Seeking replays from step 0. */
export const Op = z.union([
  z.tuple([z.literal("set"), Path, Val]),
  z.tuple([z.literal("del"), Path]),
]);

export const Step = z.object({
  line: z.number(), // index into approach.source
  note: z.string().nullable(),
  ops: z.array(Op),
});

export const Variant = z.object({
  /** Convention is typical | edge | worst-case; fixtures name their own cases. */
  id: z.string(),
  label: z.string(),
  note: z.string().nullish(),
  result: Val,
  steps: z.array(Step).min(1),
});

export const Approach = z.object({
  id: z.string(),
  label: z.string(),
  complexity: z.object({ time: z.string(), space: z.string() }),
  /**
   * Only overrides — unlisted vars render by value type. Either a bare kind
   * (`grid`, `stack`, `queue`, `heap`, `bits`, `graph`, `trie`, `intervals`,
   * `node`, `recursion`) or `role:host` attaching one var to another
   * (`pointer:nums`, `row:dp`, `cells:grid`, `labels:adj`, `marked:adj`).
   */
  viz: z.record(z.string()),
  /** Static coordinates for vars the renderer can't lay out itself (graphs). */
  layout: z.record(z.record(z.tuple([z.number(), z.number()]))),
  source: z.array(z.string()),
  variants: z.array(Variant).min(1),
});

export const Problem = z.object({
  schemaVersion: z.literal(SCHEMA_VERSION),
  slug: z.string(),
  title: z.string(),
  pattern: z.string(),
  /** Fixtures carry no difficulty, LeetCode number or prompt. */
  difficulty: z.enum(["Easy", "Medium", "Hard"]).optional(),
  leetcode: z.number().optional(),
  prompt: z.string().optional(),
  approaches: z.array(Approach).min(1),
});

export const Index = z.array(
  Problem.pick({ slug: true, title: true, pattern: true }).extend({
    difficulty: z.enum(["Easy", "Medium", "Hard"]),
  })
);

export type Op = z.infer<typeof Op>;
export type Step = z.infer<typeof Step>;
export type Variant = z.infer<typeof Variant>;
export type Approach = z.infer<typeof Approach>;
export type Problem = z.infer<typeof Problem>;
