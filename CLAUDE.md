# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
pnpm dev              # Next.js dev server (uses .next)
pnpm trace            # regenerate every trace in traces/ from content/problems/
python3 tracer/build.py two-sum reverse-linked-list   # regenerate only these slugs
pnpm check            # correctness gate: approaches, content sweep, schema freshness
pnpm test             # gate-order / quota / redaction / generation tests for /api/solve
pnpm schema           # regenerate prompts/solve-schema.json from lib/schema.ts
pnpm build            # schema freshness check, pnpm trace, then `next build` into .next-build
```

`pnpm build` writes to `.next-build` (via `NEXT_DIST`) on purpose — a production
build must not clobber a running dev server's `.next`.

There is no test *framework* — no pytest, no vitest, no fixtures. There are two
suites, both plain scripts of `assert`-style checks that exit non-zero:

- `pipeline/check.py` (`pnpm check`) asserts every approach of a problem returns
  the same result on every variant, so no expected outputs are maintained
  anywhere. It also sweeps for content gaps.
- `pipeline/test_solve.py` (`pnpm test`) covers `/api/solve`: gate order, quota,
  the spend cap, BYO-key redaction, and the generation layer — wire round-trip,
  semantic validation, the repair cap and prompt ordering. Every check there
  runs offline; `_gen.call` is the only place an HTTP request happens.

Never weaken an assertion to make something pass — fix the source.

## Architecture

Python traces the algorithms ahead of time; the browser only replays JSON. There
is no Python in the browser and no layout computation on the client.

```
content/problems/<slug>/solution.py  →  tracer/build.py  →  traces/<slug>.json  →  Next.js
```

Traces are committed build artifacts. `traces/index.json` is the whole roadmap
(built from `pipeline/seed.py`, not from what exists), so unauthored problems
still appear greyed out.

### The tracer (`tracer/leetviz.py`)

`sys.settrace` line hooks diff the frame locals between lines and emit
`["set", path, value]` / `["del", path]` ops. Two things are easy to get wrong:

- **Ops attach to the previous line.** A line event fires *before* the line runs,
  so `record()` holds `pending` and emits the diff against the line that just
  finished.
- **Every function in the file is followed**, not just the entry point. Problems
  whose real work lives in a `_walk`/`_dfs` helper would otherwise produce a
  3-step trace of the wrapper — silently shallow and still passing checks. All
  functions that actually ran are laid into one `source` listing and step line
  numbers are remapped into it.

Two reserved state keys carry structure the diff can't express as plain values:
`$nodes` (object graph, `{"$ref": nid}` edges) and `$calls` (recursion call
tree, only emitted when more than one call happened). Pointer redirection is
just a `set` on a `$nodes` path — no new op types were needed for lists, trees,
graphs, heaps, tries or call trees.

Coordinates are baked in Python: `structs.layout_tree` assigns tree x/y at
construction (x = in-order slot, y = depth), graphs get `circle_layout`. There
are deliberately no layout dependencies (no networkx, no d3-force).

`MAX_STEPS = 4000`; the per-file budget is 150 KB **gzipped**, checked in
`build.py`.

### Solution file contract

Each `content/problems/<slug>/solution.py` defines three module globals:

- `META` — slug, title, pattern, difficulty, leetcode, prompt, examples,
  constraints, and optional `unordered: True` when the answer is a set (the
  cross-check then compares order-insensitively; do not sort blanket-wide, that
  would hide real ordering bugs in problems like Spiral Matrix).
- `VARIANTS` — three, ids `typical` / `edge` / `worst-case`. `input` is a dict,
  or a zero-arg callable when the input holds nodes the algorithm mutates.
- `APPROACHES` — id, label, fn, complexity, and `viz`.

Narration comes from `#>` comments in the solution source: on a code line it
annotates that line, on its own line it annotates the next. The markers are
stripped from the listing the UI shows.

### `viz` specs

`viz` holds overrides only — unlisted vars render by value type. A value is
either a bare kind (`grid`, `stack`, `queue`, `heap`, `bits`, `graph`, `trie`,
`intervals`, `node`, `recursion`) or `role:host`, attaching one var to another
(`pointer:nums`, `row:dp`, `cells:grid`, `labels:adj`, `marked:adj`).

### Frontend

`lib/schema.ts` is the frozen `schemaVersion: 1` zod schema. `lib/traces.ts`
parses on read, which makes `next build` the schema verification step — a bad
trace fails the build rather than the page.

`lib/fold.ts` `stateAt()` replays ops from step 0 on every seek. No inverse ops,
no snapshots; scrubbing backwards is the same code path as forwards. Keep it
that way unless a few thousand ops per seek actually measures as slow.

Thirteen declared renderer kinds collapse into four components: `Diagram.tsx`
(one SVG for everything node-shaped, with `fromNodes`/`fromCalls`/`fromGraph`/
`fromHeap`/`fromTrie` adapters), `Flat.tsx` (cells, grid, intervals, map,
scalar), `Stage.tsx` (dispatch, parses `viz`), `Viewer.tsx` (tabs, source panel,
player).

`/dev/gallery/[kind]` renders the hand-written `fixtures/*.py` programs — that's
where renderers get exercised against degenerate cases without real content.
Note Next.js treats `_`-prefixed folders as private, hence `dev` not `_dev`.

### `/solve` and the cost guards

The deploy target is Vercel, not Pages — there is no `output: "export"` and no
`basePath`. `/`, `/p/[slug]` and the gallery still prerender as static HTML;
only `/s/[hash]` renders on demand, and it fetches everything client-side.

Server code is Python in `/api/*.py` at the repo root (Vercel's runtime
convention, wired up in `vercel.json`), not in `app/`. `api/_lib.py` is the one
place KV is touched and the one place the gate chain lives:

```
turnstile → normalize+hash → cache → quota → monthly cap → generate → record
```

`solve()` appends every gate it enters to an `audit` list and `pipeline/
test_solve.py` asserts on that list, so reordering the gates fails the test even
when every status code is unchanged. Two invariants that pass silently if broken:
a cache hit must not touch quota or spend, and a bring-your-own key must never
reach KV, a log line or an error body. Both have tests; keep them.

### The generation layer (`api/_gen.py`)

`_lib` decides *whether* generation runs; `_gen` is what runs. It is imported
lazily from inside `_lib`'s functions so the cycle stays one-directional.

**The model emits the trace directly. No generated code is ever executed, so
there is no sandbox and nothing to sandbox.** Validation replays ops as data.

**The API schema is derived, never written.** `pipeline/schema-json.mts` walks
the zod tree in `lib/schema.ts` and emits `prompts/solve-schema.json`;
`pnpm check` and `pnpm build` both fail if the committed artifact is stale. Two
hand-maintained schemas would drift, and a drifted schema generates traces the
player cannot parse. Node's type stripping runs the `.mts` directly — no build
step, no dependency, and `.mts` keeps it out of tsconfig's `**/*.ts`.

Strict mode cannot express three things schemaVersion 1 uses, so the transform
rewrites them and `_gen._wire` reverses each one from the same artifact:

| frozen schema | wire form | why |
| --- | --- | --- |
| optional key | required + nullable, `x-optional` | strict has no optional keys |
| `z.tuple([a,b])` | `{"_0":a,"_1":b}` | no `prefixItems` in strict |
| `z.record(v)` | `{"$entries":[{key,value}]}` | `additionalProperties` must be false |

The `$entries` wrapper is not decoration: a bare pair array would be
indistinguishable from a genuine array of two-key objects inside `Val`.
`x-*` keys are stripped before the schema reaches the API.

Because strict mode makes malformed JSON structurally impossible, there is no
JSON parse-and-retry anywhere — a fallback there would only hide a real bug.
Failure means **semantic** failure, and `_gen.validate` is where it is caught:
it replays every variant the way `lib/fold.ts` `stateAt` does and reports
out-of-range `line` indices, op paths whose parent does not exist yet, empty
arrays where the frozen schema says `.min(1)` (strict mode drops `min`), a last
step that is not a `return`, and a `return <name>` whose replayed value
disagrees with the declared `result`. That last check is skipped when the value
is a `$nodes` `{"$ref": …}` handle; on the 576 committed variants it is decidable
for 290 and disagrees on none.

A failing trace escalates to `OPENAI_MODEL_REPAIR` **at most twice**, then 502s.

**Prompt order is a cost decision, not a style one.** Static system prompt →
static context (renderer kinds + a few-shot exemplar built by *encoding* a
committed trace, so it cannot drift) → the user's problem, last. Nothing
per-request may precede the static blocks: a request id or timestamp in front of
them changes the prefix on every call and OpenAI's automatic prompt cache never
hits. Repair turns are appended after the user message so the prefix survives
them. `cached_tokens` is logged per call and totalled on `/admin/spend`, so the
regression is visible rather than merely expensive. `pnpm test` asserts the
static prefix is byte-identical across two different problems.

`prompts/solve-system.md` is read at request time — iterate it without a
redeploy — and identified by a content hash. That hash is recorded per
generation (`promptver:<hash>` in KV, `promptVersion` in the response body) so a
bad trace names the prompt that produced it.

**Model names live only in `.env`.** `_gen.model("GENERATE")` reads
`OPENAI_MODEL_GENERATE`; there is no model literal anywhere in `api/` or
`pipeline/`. With none configured, generation serves the committed two-sum trace
with a loud warning and refuses outright in production — the same shim shape as
`_FileKV`, not a second generator.

Reasoning tokens bill as output but never appear in the response, so
`/admin/spend` reports `outputTokensMonthBilled` and `outputTokensMonthVisible`
separately; conflating them under-reports cost. Real dollars come from
`SOLVE_PRICE_*_PER_MTOK`; with those blank every call falls back to
`SOLVE_STUB_COST_USD`, because an unpriced call must not count as free or the
cap stops capping.

One honest wart: the cheap normalize model runs on the **hash** gate, which is
before the **cache** gate, so it bills a few tokens even on a cache hit. Those
tokens are counted in `normalizeSpendMonthUsd`, apart from `spend:<month>`, so
the invariant that a cache hit costs the generation budget nothing still holds
exactly. It also means the cache key depends on a model's output; that is stable
in practice, and a drift shows up as a cache miss, never as a wrong trace.

### Providers and failover

`api/_gen.py` talks to OpenAI first and falls back to NVIDIA NIM, which speaks
the same chat-completions protocol, so only the base URL, key and model names
differ. Both are `Provider` instances; there are no model literals anywhere.

Failover fires on 429 and 5xx only. A 400 is our own malformed request and must
surface, so note that `HTTPError` subclasses `URLError` and has to be tested
first or a 400 gets misreported as an outage. A trace that will not replay is
also never failed over: a weaker model is not the fix and it doubles the bill.
A bring-your-own key pins OpenAI, so a BYO request can never spend our NVIDIA
credit. All four rules have tests.

The one real asymmetry: `strict: true` is an OpenAI feature. On NIM the JSON
schema is a request rather than a contract, so malformed JSON is possible again.
The OpenAI path still parses unguarded on purpose — a fallback there would hide
a real bug — while the NIM path raises into the existing repair ladder, so there
is one recovery mechanism rather than two.

NVIDIA keys are `nvapi-` prefixed. `_lib._SK_RE` and the CI bundle scan match
both prefixes; a pattern that only knew `sk-` would let one straight through.
`/admin/spend` reports `generationsByProvider` so a permanent silent failover is
visible rather than looking like business as usual.

## Content rules

LeetCode and NeetCode problem statements are copyrighted. Slugs, titles,
numbers, difficulties and pattern groupings are facts and are used; every
prompt, example and narration line in this repo is original. The official
wording is reached by outbound link — `pipeline/seed.py` `LC_SLUG` maps the
seven slugs where ours differs from LeetCode's so those links don't 404.
