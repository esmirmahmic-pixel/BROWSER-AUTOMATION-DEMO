"""Run a reproducible synthetic business workflow from intake to dashboard."""
import argparse
import json
from pathlib import Path

from business_v4.dashboard import build
from business_v4.orders import connect, create_order
from business_v4.worker import run_batch


def run_demo(workspace: str | Path) -> dict:
    root = Path(workspace)
    root.mkdir(parents=True, exist_ok=True)
    db_path = root / "demo-orders.sqlite3"
    orders = [
        ("DEMO-001", "Example Customer A", 1299),
        ("DEMO-002", "Example Customer B", 2499),
        ("DEMO-003", "Example Customer C", 999),
    ]
    with connect(db_path) as db:
        for order_id, customer, amount in orders:
            create_order(db, order_id, customer, amount)
    worker_result = run_batch(db_path)
    report = build(db_path, root / "dashboard")
    return {"worker": worker_result, "dashboard": report["counts"],
            "dashboard_path": str(root / "dashboard" / "index.html")}


def main():
    parser = argparse.ArgumentParser(description="Synthetic V4 end-to-end demo")
    parser.add_argument("--output", default="v4-demo-output")
    args = parser.parse_args()
    print(json.dumps(run_demo(args.output), indent=2))


if __name__ == "__main__":
    main()
