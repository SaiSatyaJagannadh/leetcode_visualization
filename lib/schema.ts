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
  id: z.enum(["typical", "edge", "worst-case"]),
  label: z.string(),
  input: z.record(Val),
  result: Val,
  steps: z.array(Step),
});

export const Approach = z.object({
  id: z.string(),
  label: z.string(),
  complexity: z.object({ time: z.string(), space: z.string() }),
  /** Only overrides. Unlisted vars render by value type. e.g. `{ i: "pointer:nums" }` */
  viz: z.record(z.string()),
  source: z.array(z.string()),
  variants: z.array(Variant).min(1),
});

export const Problem = z.object({
  schemaVersion: z.literal(SCHEMA_VERSION),
  slug: z.string(),
  title: z.string(),
  pattern: z.string(),
  difficulty: z.enum(["Easy", "Medium", "Hard"]),
  leetcode: z.number(),
  prompt: z.string(),
  approaches: z.array(Approach).min(1),
});

export const Index = z.array(Problem.pick({ slug: true, title: true, pattern: true, difficulty: true }));

export type Op = z.infer<typeof Op>;
export type Step = z.infer<typeof Step>;
export type Variant = z.infer<typeof Variant>;
export type Approach = z.infer<typeof Approach>;
export type Problem = z.infer<typeof Problem>;
