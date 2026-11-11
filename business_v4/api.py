"""Local-only demonstration REST API. Not a production internet-facing service."""
import json
import hmac
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, unquote
from business_v4.orders import connect, create_order, summary

MAX_BODY = 8192

def make_handler(db_path: str | Path, token: str):
    if not token:
        raise ValueError("API token required")
    class Handler(BaseHTTPRequestHandler):
        def respond(self, code, payload):
            data = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(data)

        def authorized(self):
            return hmac.compare_digest(self.headers.get("Authorization", ""), "Bearer " + token)

        def do_GET(self):
            if not self.authorized():
                return self.respond(401, {"error": "unauthorized"})
            path = urlsplit(self.path).path
            with connect(db_path) as db:
                if path == "/health":
                    return self.respond(200, {"status": "ok"})
                if path == "/api/orders/summary":
                    return self.respond(200, summary(db))
                if path.startswith("/api/orders/"):
                    order_id = unquote(path[len("/api/orders/"):])
                    if not order_id or len(order_id) > 100 or "/" in order_id:
                        return self.respond(400, {"error": "invalid order ID"})
                    row = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
                    return self.respond(200, dict(row)) if row else self.respond(404, {"error": "not found"})
            return self.respond(404, {"error": "not found"})

        def do_POST(self):
            if not self.authorized():
                return self.respond(401, {"error": "unauthorized"})
            if urlsplit(self.path).path != "/api/orders":
                return self.respond(404, {"error": "not found"})
            try:
                length = int(self.headers.get("Content-Length", "-1"))
                if length < 0 or length > MAX_BODY:
                    return self.respond(413, {"error": "invalid body size"})
                if self.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
                    return self.respond(415, {"error": "JSON required"})
                raw = self.rfile.read(length)
                data = json.loads(raw)
                if not isinstance(data, dict) or set(data) != {"id", "customer", "amount_cents"}:
                    return self.respond(400, {"error": "invalid payload"})
                with connect(db_path) as db:
                    row = create_order(db, data["id"], data["customer"], data["amount_cents"])
                return self.respond(200, row)
            except (ValueError, TypeError, UnicodeError, json.JSONDecodeError):
                return self.respond(400, {"error": "invalid order"})

        def log_message(self, format, *args):
            pass
    return Handler

def serve():
    token = os.environ.get("V4_API_TOKEN")
    if not token:
        raise SystemExit("Set V4_API_TOKEN before starting the demo API")
    db_path = os.environ.get("V4_DB_PATH", "v4_orders.sqlite3")
    server = ThreadingHTTPServer(("127.0.0.1", 8766), make_handler(db_path, token))
    print("V4 local demo API on 127.0.0.1:8766", flush=True)
    server.serve_forever()

if __name__ == "__main__":
    serve()
