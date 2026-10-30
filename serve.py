#!/usr/bin/env python3
"""Minimal dashboard for a local screenpipe recorder.

Serves index.html and proxies read-only API calls to screenpipe
(localhost:3030), adding the API token server-side so it never
reaches the browser. Standard library only.
"""
import os
import subprocess
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
PORT = int(os.environ.get("DASHBOARD_PORT", "3031"))
API = os.environ.get("SCREENPIPE_API", "http://127.0.0.1:3030")
BIN = os.environ.get(
    "SCREENPIPE_BIN", str(Path.home() / "src/screenpipe/target/release/screenpipe")
)
# Only these API paths are reachable through the proxy.
ALLOWED = ("/search", "/frames/")


def load_token():
    token = os.environ.get("SCREENPIPE_API_KEY")
    if token:
        return token
    out = subprocess.run([BIN, "auth", "token"], capture_output=True, text=True, check=True)
    return out.stdout.strip().splitlines()[-1]


TOKEN = load_token()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(HERE), **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self.proxy(self.path[4:])
        if self.path in ("/", "/index.html"):
            return super().do_GET()
        self.send_error(404)

    def proxy(self, path):
        if not path.startswith(ALLOWED):
            return self.send_error(403)
        req = urllib.request.Request(API + path, headers={"Authorization": f"Bearer {TOKEN}"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                status, ctype, body = resp.status, resp.headers.get("Content-Type"), resp.read()
        except urllib.error.HTTPError as e:
            status, ctype, body = e.code, e.headers.get("Content-Type"), e.read()
        except urllib.error.URLError as e:
            status, ctype, body = 502, "text/plain", f"screenpipe unreachable: {e.reason}".encode()
        self.send_response(status)
        self.send_header("Content-Type", ctype or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        cacheable = status == 200 and path.startswith("/frames/")
        self.send_header("Cache-Control", "private, max-age=3600" if cacheable else "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    print(f"screenpipe dashboard: http://localhost:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
