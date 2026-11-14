"""Serve the golf folder locally: python scripts/serve.py  (then open http://localhost:8765)

Opening index.html directly from disk also works; a local server is only
needed for the "Ball is here" GPS button on some browsers and for previews.
"""
import functools
import http.server
import os
from pathlib import Path

class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    """Always send the latest files, so edits show up on a plain reload."""

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


port = int(os.environ.get("PORT", "8765"))
root = Path(__file__).resolve().parent.parent
handler = functools.partial(NoCacheHandler, directory=str(root))
print(f"Serving {root} at http://localhost:{port}", flush=True)
http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()
