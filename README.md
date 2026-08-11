# leetcode_visualization

LeetViz — watch 150 LeetCode problems actually run, one line at a time.

Live Streamlit app: **https://leetviz-traces.streamlit.app** — no signup, no key.

## What it's for

Reading a solution is not the same as seeing it run. The usual way to study these
problems is to read the final code and take someone's word for what the variables
are doing; the loop that "moves a pointer inward" is a sentence, and the sentence
is where it stops making sense.

So every problem here is *executed* ahead of time and every line's effect is
recorded. Press play and the current line lights up while the real state moves
beside it — the array, the two pointers closing in, the hash map filling, the tree
being walked, the recursion stack growing and unwinding. Nothing is hand-drawn and
nothing is an approximation: each frame is the actual value the variables held at
that line.

It is for the stretch where you already know *what* the answer is and still cannot
see *why* it works — and for spotting the pattern under it, which is the part that
transfers to the problem you get asked in the interview.

## Using it

The corpus is the NeetCode 150 shape: **150 problems** across **18 patterns**
(28 Easy, 101 Medium, 21 Hard), all traced and playable.

**Find a problem.** The roadmap lists every problem grouped by pattern, with a
progress bar per group. Search by name, number or pattern — "two sum", "leetcode
25", "sliding window" all work — or filter to Easy / Medium / Hard. Problems you
have watched get ticked, so a long sitting has a visible edge.

**Watch it run.** Open one and you get the problem in original wording, a link out
to LeetCode and NeetCode for the official statement, then the player:

- **Approach tabs** — 148 of the 150 carry two, a brute force next to the
  idiomatic one, with time and space on each. The point is to watch the slow one
  be slow, so the fast one is an answer to something rather than a trick.
- **Variant tabs** — three runs of the same code: `typical`, `edge` and
  `worst-case`. Same algorithm, different input, and the edge case is usually
  where the understanding actually happens.
- **The player** — step forward and back, jump to either end, or press play and
  let it run. The source panel lights the current line; the panel beside it draws
  the live state, shaped to what the value is (cells with indices, grids, trees,
  linked lists, graphs, heaps, tries, interval bars, the recursion call tree).
- **The narration** — one line under the player saying what the step just did, so
  you are never guessing which change mattered.

**Learn the pattern.** Under the trace is the house template for its pattern — the
signal in a problem that points to it, and the shape of the solution it implies.
That comes from the `leetcode-teacher` skill in `.agents/skills/`, read off disk,
so it is the same lesson every time rather than a fresh guess. 12 of the 18
patterns have one so far, covering 108 of the 150 problems; the rest show the
trace alone.

**Ask about it.** The **Ask** view takes a question in words. Naming any of the
150 plays that trace right there and needs no model at all. With a key configured
it also answers free-form questions, and can generate a brand-new trace for a
problem outside the 150 — see [The Ask view](#the-ask-view-optional--needs-a-model-key).

See `CLAUDE.md` for how the tracing works.

## Two front ends, one set of traces

`traces/*.json` are committed build artifacts. Both readers replay the same ops.

| | run | what it is |
| --- | --- | --- |
| Next.js | `pnpm dev` → localhost:3000 | the full site: SVG player, `/solve` generation, `/admin/spend` |
| Streamlit | `streamlit run streamlit_app.py` | a single-file reader over the same traces — no server, no API keys |

The Streamlit app is deliberately smaller: problem picker, approach tabs,
variant tabs, a step slider, the source with the current line lit, and the state
drawn beside it (trees and linked lists, the recursion call tree, graphs, grids,
and index-annotated sequences). It does not carry `/solve` — generation needs the
serverless functions in `api/`, which Streamlit does not run.

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
python3 pipeline/check_streamlit.py   # replays all 150 traces through the reader
```

## Deploy the Streamlit app

Streamlit Community Cloud builds straight from this repo. No secrets are needed
for the part people come for: all 150 traces, the search and the pattern
templates are read off disk and never touch the network. Secrets only turn on the
Ask view's two model-backed modes, below.

Already deployed at https://leetviz-traces.streamlit.app — it redeploys itself
on every push to `main`. To stand up another copy: https://share.streamlit.io →
**Create app** → this repo → branch `main` → main file `streamlit_app.py`.

The Next.js site deploys separately to Vercel (`npx vercel --prod`), which is
what serves `/solve` and `/admin/spend`.

## The Ask view (optional — needs a model key)

Without secrets the Streamlit app still works: the 150 traces and the lookup box
need no network at all — naming any of the 150 plays it, and the pattern template
below it comes from the `leetcode-teacher` skill in `.agents/skills/`, read off
disk rather than generated. Adding a key turns on the **Ask** view, which has two
modes:

- **Explain** — a plain answer in words, from the cheap model.
- **Trace it** — generates a step-by-step visualization in the same shape as the
  150, using `api/_gen.py`. Same prompt, same schema, same repair ladder as the
  deployed `/solve`: there is one generator in this repo, not two.

Add these under **Manage app → Settings → Secrets** on Streamlit Cloud (locally,
`.streamlit/secrets.toml`, which is gitignored). Any one provider is enough — the
chain tries them in order and fails over on 429, 5xx, and a reply cut off at the
output cap:

```toml
GEMINI_API_KEY = "AIza…"
GEMINI_MODEL_GENERATE = "gemini-2.5-flash"
GEMINI_MODEL_CHEAP = "gemini-2.5-flash"
SOLVE_PROVIDER_ORDER = "google,openai,nvidia"

# OPENAI_API_KEY = "sk-…"
# OPENAI_MODEL_GENERATE = "gpt-5"
# NVIDIA_API_KEY = "nvapi-…"
# NVIDIA_MODEL_GENERATE = "openai/gpt-oss-20b"
```

Two things to know before you turn it on:

- **It spends your money**, and the URL is public, so it is capped twice. The
  per-session caps are the ones the page shows — `LEETVIZ_MAX_GENERATIONS`
  (default 3) and `LEETVIZ_MAX_ASKS` (default 15). Session state dies on reload,
  so those bound a polite reader and nothing else; the wall is the per-day
  budget, `LEETVIZ_DAY_GENERATIONS` (default 40) and `LEETVIZ_DAY_ASKS`
  (default 300), counted in the same store the deployed API's quota uses.
  Explain is the cheap path, but a cheap call in a loop is still a bill — both
  paths are counted, not just traces. With no KV credentials in the app's secrets
  that day counter is a file in the container's `/tmp`, so a restart resets it;
  add `KV_REST_API_URL` and `KV_REST_API_TOKEN` to make it survive one and share
  a budget with the deployed API.
- **A weak `*_MODEL_GENERATE` will fail.** The trace is validated by replaying it
  the way the player does, and one that does not replay is refused after two
  repair attempts rather than shown. On `gemini-2.5-flash` that happens on
  problems a stronger model handles.
