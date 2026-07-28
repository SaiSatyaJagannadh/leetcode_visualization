#!/usr/bin/env python3
"""Regenerate every trace in content/problems/ into traces/."""

import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import leetviz

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "traces"


def load(path):
    spec = importlib.util.spec_from_file_location(path.parent.name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    OUT.mkdir(exist_ok=True)
    only = sys.argv[1:] or None
    index = []
    for sol in sorted(ROOT.glob("content/problems/*/solution.py")):
        slug = sol.parent.name
        if only and slug not in only:
            continue
        obj = leetviz.build_problem(load(sol))
        dest = OUT / f"{slug}.json"
        leetviz.dump(obj, dest)
        kb = dest.stat().st_size / 1024
        print(f"{slug:28} {len(obj['approaches'])} approaches  {kb:6.1f} KB")
        index.append({k: obj[k] for k in ("slug", "title", "pattern", "difficulty")})
    if not only:
        leetviz.dump(sorted(index, key=lambda p: p["title"]), OUT / "index.json")


if __name__ == "__main__":
    main()
