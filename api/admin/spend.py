"""GET /api/admin/spend — real KV counters. Shared-secret header, closed by default."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _lib  # noqa: E402


class handler(_lib.JSONHandler):
    def do_GET(self):
        if not _lib.admin_ok(self.headers.get("x-admin-secret")):
            return self.reply(401, {"error": "unauthorized"})
        self.reply(200, _lib.spend_report())
