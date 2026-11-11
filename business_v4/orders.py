"""Transactional, idempotent order intake and processing with SQLite."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ALLOWED = {"pending", "completed", "failed"}


def connect(path: str | Path) -> sqlite3.Connection:
    db = sqlite3.connect(str(path), timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA busy_timeout=10000")
    db.execute("""CREATE TABLE IF NOT EXISTS orders (
        id TEXT PRIMARY KEY,
        customer TEXT NOT NULL,
        amount_cents INTEGER NOT NULL CHECK(amount_cents > 0),
        status TEXT NOT NULL DEFAULT 'pending',
        attempts INTEGER NOT NULL DEFAULT 0,
        last_error TEXT,
        created_at TEXT NOT NULL
    )""")
    db.commit()
    return db


def create_order(db: sqlite3.Connection, order_id: str, customer: str, amount_cents: int) -> dict:
    if not isinstance(order_id, str) or not order_id.strip() or len(order_id) > 100:
        raise ValueError("Invalid order ID")
    if not isinstance(customer, str) or not customer.strip() or len(customer) > 200:
        raise ValueError("Invalid customer")
    if type(amount_cents) is not int or amount_cents <= 0 or amount_cents > 100_000_000:
        raise ValueError("Invalid amount")
    with db:
        db.execute(
            "INSERT OR IGNORE INTO orders(id,customer,amount_cents,created_at) VALUES(?,?,?,?)",
            (order_id, customer, amount_cents, datetime.now(timezone.utc).isoformat()),
        )
    row = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    if row["customer"] != customer or row["amount_cents"] != amount_cents:
        raise ValueError("Order ID already used with different payload")
    return dict(row)


def process_next(db: sqlite3.Connection, *, max_attempts: int = 3, simulate_failure: bool = False) -> dict | None:
    if type(max_attempts) is not int or max_attempts < 1:
        raise ValueError("Invalid max_attempts")
    db.execute("BEGIN IMMEDIATE")
    try:
        row = db.execute(
            "SELECT * FROM orders WHERE status='pending' AND attempts < ? ORDER BY created_at,id LIMIT 1",
            (max_attempts,),
        ).fetchone()
        if row is None:
            db.commit()
            return None
        attempts = row["attempts"] + 1
        status = "failed" if simulate_failure and attempts >= max_attempts else (
            "pending" if simulate_failure else "completed"
        )
        error = "Simulated transient error" if simulate_failure else None
        db.execute(
            "UPDATE orders SET status=?, attempts=?, last_error=? WHERE id=?",
            (status, attempts, error, row["id"]),
        )
        db.commit()
        return dict(db.execute("SELECT * FROM orders WHERE id=?", (row["id"],)).fetchone())
    except Exception:
        db.rollback()
        raise


def summary(db: sqlite3.Connection) -> dict:
    rows = db.execute("SELECT status,COUNT(*) AS count FROM orders GROUP BY status").fetchall()
    counts = {status: 0 for status in ALLOWED}
    counts.update({row["status"]: row["count"] for row in rows})
    return {"total": sum(counts.values()), **counts}


def export_summary(db: sqlite3.Connection, output: str | Path) -> None:
    Path(output).write_text(json.dumps(summary(db), indent=2), encoding="utf-8")
