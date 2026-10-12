"""Dependency-free loopback demo adapter. Never expose this server publicly."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from .store import Store, Conflict

ROOT = Path(__file__).resolve().parents[1]
FILES = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"),
         "/style.css": ("style.css", "text/css")}
MAX_BODY = 8192


def make_server(database, port=8080):
    store = Store(database)

    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(5)

        def send(self, status, body, mime="application/json"):
            payload = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", mime + "; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/api/health":
                self.send(200, {"status": "ok", "version": "0.1.0-demo", "mode": "simulation"})
            elif path == "/api/state":
                self.send(200, store.snapshot())
            elif path in FILES:
                name, mime = FILES[path]
                self.send(200, (ROOT / "web" / name).read_bytes(), mime)
            else:
                self.send(404, {"error": "not_found"})

        def do_POST(self):
            # Block foreign browser origins and require JSON. Loopback-only is not production auth.
            origin = self.headers.get("Origin")
            local_origins = {f"http://127.0.0.1:{self.server.server_port}", f"http://localhost:{self.server.server_port}"}
            if origin and origin not in local_origins:
                return self.send(403, {"error": "foreign_origin"})
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                return self.send(415, {"error": "application/json required"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= MAX_BODY:
                    return self.send(413, {"error": "body must contain 1-8192 bytes"})
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError("JSON object required")
                path = urlsplit(self.path).path
                if path == "/api/demo/scan":
                    result = store.scan(data)
                elif path == "/api/demo/clear":
                    result = store.clear()
                elif path == "/api/plates/add":
                    result = store.change_plate(data.get("plate"))
                elif path == "/api/plates/remove":
                    result = store.change_plate(data.get("plate"), add=False)
                else:
                    return self.send(404, {"error": "not_found"})
                self.send(200, result)
            except Conflict as exc:
                self.send(409, {"error": str(exc)})
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                self.send(400, {"error": str(exc)})

        def log_message(self, fmt, *args):
            # HTTP status and path only, no observation payloads or secrets.
            super().log_message(fmt, *args)

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--db", default=str(ROOT / "data" / "demo.sqlite3"))
    args = parser.parse_args()
    server = make_server(args.db, args.port)
    print(f"Simulation demo: http://127.0.0.1:{server.server_port} (no OCR / no hardware)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
