#!/usr/bin/env python3
"""Regenerate every trace in content/problems/ into traces/."""

import gzip
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
import leetviz
import seed

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "traces"


def load(path):
    spec = importlib.util.spec_from_file_location(path.parent.name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "_fixtures").mkdir(exist_ok=True)
    only = sys.argv[1:] or None
    index = []
    sources = [(p, False) for p in sorted(ROOT.glob("content/problems/*/solution.py"))]
    sources += [(p, True) for p in sorted(ROOT.glob("fixtures/*.py"))]

    for src, is_fixture in sources:
        slug = src.stem if is_fixture else src.parent.name
        if only and slug not in only:
            continue
        obj = leetviz.build_problem(load(src))
        dest = OUT / ("_fixtures" if is_fixture else "") / f"{slug}.json"
        leetviz.dump(obj, dest)
        kb = len(gzip.compress(dest.read_bytes())) / 1024  # the budget is gzipped
        steps = max(len(v["steps"]) for a in obj["approaches"] for v in a["variants"])
        print(f"{slug:22} {len(obj['approaches'])} approaches  {steps:5} steps  {kb:6.1f} KB")
        if kb > 150:
            print(f"  !! {slug} is over the 150 KB budget")
        if not is_fixture:
            index.append({k: obj[k] for k in ("slug", "title", "pattern", "difficulty")})
    if not only:
        # The index is the whole roadmap, not just what's authored — an unbuilt
        # problem still shows in its pattern, greyed out, so the gap is visible.
        done = {p["slug"] for p in index}
        roadmap = [
            {
                "slug": slug,
                "title": title,
                "pattern": pattern,
                "difficulty": diff,
                "leetcode": num,
                "ready": slug in done,
            }
            for slug, title, pattern, diff, num, _, _ in seed.rows()
        ]
        missing = [p["slug"] for p in index if p["slug"] not in {r["slug"] for r in roadmap}]
        if missing:
            print(f"  !! not in seed: {', '.join(missing)}")
        leetviz.dump({"patterns": seed.PATTERNS, "problems": roadmap}, OUT / "index.json")
        print(f"\n{len(done)} / {len(roadmap)} authored")
        names = [p.stem for p in sorted(ROOT.glob("fixtures/*.py"))]
        leetviz.dump(names, OUT / "_fixtures" / "index.json")


if __name__ == "__main__":
    main()
