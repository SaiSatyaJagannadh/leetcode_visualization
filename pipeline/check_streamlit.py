"""Replay every committed trace through the Streamlit reader.

`streamlit_app.py` re-implements `lib/fold.ts` in Python. Two readers of the same
artifacts is exactly the kind of thing that drifts silently, so this walks every
step of every variant of every trace: the fold must not dangle a path, the step
line must index into the source, and the renderer must survive every shape the
corpus contains.

    python3 pipeline/check_streamlit.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from streamlit_app import render_state, source_html, state_at, touched  # noqa: E402

fails = []
traces = sorted((ROOT / "traces").glob("*.json"))
steps_seen = 0

for path in traces:
    if path.name == "index.json":
        continue
    trace = json.loads(path.read_text())
    for approach in trace["approaches"]:
        source, viz, layout = approach["source"], approach["viz"], approach["layout"]
        for variant in approach["variants"]:
            steps = variant["steps"]
            where = f'{trace["slug"]}/{approach["id"]}/{variant["id"]}'
            for i, step in enumerate(steps):
                if not 0 <= step["line"] < len(source):
                    fails.append(f'{where} step {i}: line {step["line"]} outside source')
                    continue
                try:
                    state = state_at(steps, i)
                    source_html(source, step["line"])
                    render_state(state, viz, layout, touched(step))
                except Exception as e:  # noqa: BLE001 — any crash is the failure
                    fails.append(f"{where} step {i}: {type(e).__name__}: {e}")
                steps_seen += 1

print(f"{len(traces) - 1} traces, {steps_seen} steps replayed")
for f in fails[:20]:
    print("  FAIL", f)
if fails:
    print(f"{len(fails)} failures")
    sys.exit(1)
print("streamlit reader: ok")
