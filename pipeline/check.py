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
sys.exit(1 if failed else 0)
