"""GET /api/share?h=<hash> — read side of the solve cache, for /s/[hash] links.

There is no write side: /api/solve already stores every trace it generates under
its prompt hash, so a share link is just that hash.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lib  # noqa: E402


class handler(_lib.JSONHandler):
    def do_GET(self):
        h = self.query("h")
        if not h.isalnum():
            return self.reply(400, {"error": "bad hash"})
        cached = _lib.store.get(f"cache:{h}")
        if not cached:
            return self.reply(404, {"error": "no trace for that link"})
        self.reply(200, {"hash": h, "cached": True, "trace": json.loads(cached)})
