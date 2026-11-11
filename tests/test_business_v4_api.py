"""HTTP integration tests for the local demo API."""
import json
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from business_v4.api import make_handler


@pytest.fixture
def api(tmp_path):
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmp_path / "api.db", "test-token"))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield "http://127.0.0.1:" + str(server.server_port)
    server.shutdown()
    server.server_close()
    thread.join(timeout=3)


def request(base, path, method="GET", data=None, token="test-token"):
    body = json.dumps(data).encode() if data is not None else None
    headers = {"Authorization": "Bearer " + token}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = Request(base + path, data=body, headers=headers, method=method)
    try:
        with urlopen(req, timeout=3) as response:
            return response.status, json.load(response)
    except HTTPError as exc:
        return exc.code, json.load(exc)


def test_unauthorized(api):
    assert request(api, "/api/orders/summary", token="wrong")[0] == 401


def test_order_api_roundtrip(api):
    order = {"id": "demo-1", "customer": "Example", "amount_cents": 1299}
    assert request(api, "/api/orders", "POST", order)[0] == 200
    assert request(api, "/api/orders", "POST", order)[0] == 200
    assert request(api, "/api/orders/demo-1")[1]["amount_cents"] == 1299
    assert request(api, "/api/orders/summary")[1]["total"] == 1


def test_invalid_payload(api):
    assert request(api, "/api/orders", "POST", {"id": "x"})[0] == 400


def test_missing_order(api):
    assert request(api, "/api/orders/absent")[0] == 404


def test_duplicate_conflict(api):
    first = {"id": "x", "customer": "Example", "amount_cents": 100}
    second = {**first, "amount_cents": 200}
    assert request(api, "/api/orders", "POST", first)[0] == 200
    assert request(api, "/api/orders", "POST", second)[0] == 400
