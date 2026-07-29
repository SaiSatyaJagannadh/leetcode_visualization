"""POST /api/solve — the gated generation endpoint. Gate order lives in _lib.solve()."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _lib  # noqa: E402


class handler(_lib.JSONHandler):
    def do_POST(self):
        body = self.payload()
        sid, set_cookie = self.session()
        # The BYO key is read straight out of the header into a local and is
        # never written to KV, never logged and never echoed in a response.
        byo = self.headers.get("x-byo-key") or None
        status, out, audit = _lib.solve(
            prompt=body.get("prompt", ""),
            turnstile_token=body.get("turnstileToken"),
            session_id=sid,
            ip=self.client_ip(),
            byo_key=byo,
        )
        _lib.log(f"solve {status} gates={'>'.join(audit)} byo={bool(byo)}", byo)
        self.reply(status, out, set_cookie)
