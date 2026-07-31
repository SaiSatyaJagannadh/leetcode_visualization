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
