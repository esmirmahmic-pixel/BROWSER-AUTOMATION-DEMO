"""Static V4 dashboard regression tests."""
import json

from business_v4.dashboard import build, render
from business_v4.orders import connect, create_order, process_next


def test_empty_dashboard(tmp_path):
    report = build(tmp_path / "empty.db", tmp_path / "site")
    assert report["counts"]["total"] == 0
    assert "No demo orders yet" in (tmp_path / "site" / "index.html").read_text()
    assert json.loads((tmp_path / "site" / "summary.json").read_text())["demo_only"] is True


def test_dashboard_escapes_customer_html(tmp_path):
    path = tmp_path / "orders.db"
    with connect(path) as db:
        create_order(db, "id-1", "<script>alert(1)</script>", 2500)
    build(path, tmp_path / "site")
    page = (tmp_path / "site" / "index.html").read_text()
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page


def test_dashboard_counts_and_snapshot(tmp_path):
    path = tmp_path / "orders.db"
    with connect(path) as db:
        create_order(db, "id-1", "Demo", 100)
        create_order(db, "id-2", "Demo", 200)
        process_next(db)
    report = build(path, tmp_path / "site")
    assert report["counts"] == {"total": 2, "pending": 1, "completed": 1, "failed": 0}
    assert len(report["recent_orders"]) == 2
    assert (tmp_path / "site" / "index.html").is_file()


def test_render_escapes_id(tmp_path):
    page = render({"total": 1, "pending": 1, "completed": 0, "failed": 0},
                  [{"id": "<img src=x>", "customer": "Demo", "amount_cents": 1,
                    "status": "pending", "attempts": 0}])
    assert "<img src=x>" not in page
    assert "&lt;img src=x&gt;" in page
