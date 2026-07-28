#!/usr/bin/env python3
"""Cross-check every problem: all approaches must agree on every variant.

No expected outputs to maintain — if the brute force and the clever version
disagree, one of them is wrong, and that catches almost everything worth
catching. Also flags traces that are too long to sit through.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LONG = 400  # steps; past this a trace stops being watchable

failed = []
slow = []

for path in sorted((ROOT / "traces").glob("*.json")):
    if path.name == "index.json":
        continue
    problem = json.loads(path.read_text())
    by_variant = {}
    for approach in problem["approaches"]:
        for variant in approach["variants"]:
            by_variant.setdefault(variant["id"], []).append(
                (approach["id"], variant["result"], len(variant["steps"]))
            )

    for vid, entries in by_variant.items():
        norm = sorted if problem.get("unordered") else (lambda x: x)
        results = {
            json.dumps(norm(r) if isinstance(r, list) else r, sort_keys=True)
            for _, r, _ in entries
        }
        if len(results) > 1:
            failed.append(
                f"{problem['slug']} [{vid}]: "
                + ", ".join(f"{aid}={json.dumps(r)}" for aid, r, _ in entries)
            )
        for aid, _, steps in entries:
            if steps > LONG:
                slow.append(f"{problem['slug']} {aid} [{vid}]: {steps} steps")

print(f"checked {len(list((ROOT / 'traces').glob('*.json'))) - 1} problems")
for line in slow:
    print(f"  slow  {line}")
for line in failed:
    print(f"  FAIL  {line}")
print(f"\n{len(failed)} disagreements, {len(slow)} over {LONG} steps")

# --- content sweep -------------------------------------------------------

gaps = []
for path in sorted((ROOT / "traces").glob("*.json")):
    if path.name == "index.json":
        continue
    p = json.loads(path.read_text())
    slug = p["slug"]
    if not p.get("prompt"):
        gaps.append(f"{slug}: no prompt")
    if len(p.get("examples", [])) < 2:
        gaps.append(f"{slug}: fewer than 2 examples")
    if not p.get("constraints"):
        gaps.append(f"{slug}: no constraints")
    for a in p["approaches"]:
        narrated = sum(1 for v in a["variants"] for s in v["steps"] if s["note"])
        if narrated == 0:
            gaps.append(f"{slug}/{a['id']}: no narration")
        if len(a["variants"]) < 3:
            gaps.append(f"{slug}/{a['id']}: {len(a['variants'])} variants, expected 3")

for g in gaps:
    print(f"  gap   {g}")
print(f"{len(gaps)} content gaps")

sys.exit(1 if failed or gaps else 0)
