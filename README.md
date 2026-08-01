# leetcode_visualization

LeetViz — 150 LeetCode problems traced line by line in Python ahead of time, so
the reader only replays JSON. See `CLAUDE.md` for the architecture.

Live Streamlit app: **https://leetviz-traces.streamlit.app**

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

Streamlit Community Cloud builds straight from this repo — no secrets needed,
because nothing in the Streamlit path calls a model.

Already deployed at https://leetviz-traces.streamlit.app — it redeploys itself
on every push to `main`. To stand up another copy: https://share.streamlit.io →
**Create app** → this repo → branch `main` → main file `streamlit_app.py`.

The Next.js site deploys separately to Vercel (`npx vercel --prod`), which is
what serves `/solve` and `/admin/spend`.

## The Ask view (optional — needs a model key)

Without secrets the Streamlit app still works: the 150 traces and the lookup box
need no network at all. Adding a key turns on the **Ask** view, which has two
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

- **It spends your money.** `LEETVIZ_MAX_GENERATIONS` (default 3) caps traces per
  browser session, because the URL is public. Explain answers are cheap; traces
  are not.
- **A weak `*_MODEL_GENERATE` will fail.** The trace is validated by replaying it
  the way the player does, and one that does not replay is refused after two
  repair attempts rather than shown. On `gemini-2.5-flash` that happens on
  problems a stronger model handles.
