"""End-to-end tests spanning order intake, worker and dashboard."""
import json
from concurrent.futures import ThreadPoolExecutor

from business_v4.demo import run_demo
from business_v4.orders import connect, create_order, summary
from business_v4.worker import run_batch


def test_full_demo_pipeline(tmp_path):
    result = run_demo(tmp_path)
    assert result["worker"]["completed"] == 3
    assert result["dashboard"]["completed"] == 3
    page = (tmp_path / "dashboard" / "index.html").read_text()
    assert "DEMO-001" in page
    assert "Example Customer C" in page
    assert json.loads((tmp_path / "dashboard" / "summary.json").read_text())["counts"]["total"] == 3


def test_repeated_demo_is_idempotent(tmp_path):
    run_demo(tmp_path)
    again = run_demo(tmp_path)
    assert again["worker"]["attempts_processed"] == 0
    assert again["dashboard"]["total"] == 3


def test_two_workers_do_not_double_process(tmp_path):
    path = tmp_path / "orders.db"
    with connect(path) as db:
        for i in range(30):
            create_order(db, f"job-{i}", "Example", 100)
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: run_batch(path), range(2)))
    with connect(path) as db:
        assert summary(db)["completed"] == 30
        assert db.execute("SELECT SUM(attempts) FROM orders").fetchone()[0] == 30
    assert sum(result["attempts_processed"] for result in results) == 30
