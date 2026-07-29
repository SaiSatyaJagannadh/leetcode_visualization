# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
pnpm dev              # Next.js dev server (uses .next)
pnpm trace            # regenerate every trace in traces/ from content/problems/
python3 tracer/build.py two-sum reverse-linked-list   # regenerate only these slugs
pnpm check            # correctness gate: cross-check approaches + content sweep
pnpm test             # gate-order / quota / redaction tests for /api/solve
pnpm build            # pnpm trace, then `next build` into .next-build
```

`pnpm build` writes to `.next-build` (via `NEXT_DIST`) on purpose — a production
build must not clobber a running dev server's `.next`.

There is no test framework. `pipeline/check.py` is the test suite: it asserts
every approach of a problem returns the same result on every variant, so no
expected outputs are maintained anywhere. It exits non-zero on disagreements or
content gaps. Never weaken an assertion to make something pass — fix the source.

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

Generation is a stub returning `traces/two-sum.json`. There is no OpenAI call
yet — the meter was built before the faucet on purpose.

## Content rules

LeetCode and NeetCode problem statements are copyrighted. Slugs, titles,
numbers, difficulties and pattern groupings are facts and are used; every
prompt, example and narration line in this repo is original. The official
wording is reached by outbound link — `pipeline/seed.py` `LC_SLUG` maps the
seven slugs where ours differs from LeetCode's so those links don't 404.
