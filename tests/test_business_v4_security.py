"""V4 API security regression checks."""
import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from business_v4.api import make_handler


@pytest.fixture
def api(tmp_path):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path / "db.sqlite3", "test-token"))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield "http://127.0.0.1:" + str(server.server_port)
    server.shutdown()
    server.server_close()
    thread.join(timeout=3)


def call(url, *, token="test-token", body=None, content_type="application/json"):
    headers = {"Authorization": "Bearer " + token}
    if body is not None:
        headers["Content-Type"] = content_type
    request = Request(url, data=body, headers=headers, method="POST" if body is not None else "GET")
    try:
        with urlopen(request, timeout=3) as response:
            return response.status, response.headers
    except HTTPError as error:
        return error.code, error.headers


def test_invalid_token_rejected(api):
    assert call(api + "/api/orders/summary", token="incorrect")[0] == 401


def test_json_content_type_required(api):
    body = json.dumps({"id": "x", "customer": "Demo", "amount_cents": 100}).encode()
    assert call(api + "/api/orders", body=body, content_type="text/plain")[0] == 415


def test_malformed_json_rejected(api):
    assert call(api + "/api/orders", body=b"{broken")[0] == 400


def test_encoded_slash_in_id_rejected(api):
    assert call(api + "/api/orders/a%2Fb")[0] == 400


def test_oversized_order_id_rejected(api):
    assert call(api + "/api/orders/" + "a" * 101)[0] == 400


def test_no_sniff_header(api):
    code, headers = call(api + "/health")
    assert code == 200
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["Cache-Control"] == "no-store"
