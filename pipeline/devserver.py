#!/usr/bin/env python3
"""Serve api/*.py locally, because `next dev` can't.

Those handlers are Vercel Python functions; the Next dev server has no runtime
for them, so /api/solve 404s under `pnpm dev` and the whole /solve flow looks
broken. Vercel runs them in production and `vercel dev` runs them locally, but
neither helps someone who just typed `pnpm dev`.

This mounts the SAME handler classes Vercel imports — no second implementation
of the gate chain, and nothing here ships to production. next.config.mjs
proxies /api/* here only when NODE_ENV is development.
"""

import importlib.util
import os
import sys
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORT = int(os.environ.get("DEV_API_PORT", "8787"))


def load_env():
    """Read .env into the environment. Values are never printed."""
    env = ROOT / ".env"
    if not env.exists():
        return []
    seen = []
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip("'\"")
        if value and key not in os.environ:
            os.environ[key] = value
            seen.append(key)
    return seen


def load(path):
    """Import a handler module by file path — api/ is not a package."""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.handler


def main():
    names = load_env()
    sys.path.insert(0, str(ROOT / "api"))

    routes = {
        "/api/solve": load(ROOT / "api" / "solve.py"),
        "/api/share": load(ROOT / "api" / "share.py"),
        "/api/admin/spend": load(ROOT / "api" / "admin" / "spend.py"),
    }
    import _lib

    class Dispatch(_lib.JSONHandler):
        def route(self, verb):
            target = routes.get(self.path.split("?")[0])
            if target is None:
                return self.reply(404, {"error": "no such route"})
            fn = getattr(target, verb, None)
            if fn is None:
                return self.reply(405, {"error": "method not allowed"})
            # Delegate unbound: every target subclasses JSONHandler, so `self`
            # already carries the machinery the method expects.
            fn(self)

        def do_GET(self):
            self.route("do_GET")

        def do_POST(self):
            self.route("do_POST")

    print(f"dev api on :{PORT}  routes={' '.join(sorted(routes))}")
    print(f"loaded from .env: {' '.join(names) if names else '(nothing)'}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Dispatch).serve_forever()


if __name__ == "__main__":
    main()
