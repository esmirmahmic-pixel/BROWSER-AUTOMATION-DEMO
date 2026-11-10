"""SQLite-backed execution history for the browser automation demo."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('passed', 'failed')),
    duration_ms INTEGER NOT NULL CHECK(duration_ms >= 0),
    error TEXT,
    created_at TEXT NOT NULL
)
"""

def record_run(db_path: str | Path, task: str, status: str, duration_ms: int, error: str | None = None) -> int:
    if status not in {"passed", "failed"}:
        raise ValueError("status must be 'passed' or 'failed'")
    if not task.strip() or duration_ms < 0:
        raise ValueError("task must be nonempty and duration_ms nonnegative")
    if status == "passed" and error:
        raise ValueError("passed runs cannot contain an error")
    with sqlite3.connect(db_path) as connection:
        connection.execute(SCHEMA)
        cursor = connection.execute(
            "INSERT INTO runs (task, status, duration_ms, error, created_at) VALUES (?, ?, ?, ?, ?)",
            (task, status, duration_ms, error, datetime.now(timezone.utc).isoformat()),
        )
        return int(cursor.lastrowid)

def summarize(db_path: str | Path) -> dict:
    with sqlite3.connect(db_path) as connection:
        connection.execute(SCHEMA)
        total, passed, failed, average_ms = connection.execute(
            """SELECT COUNT(*), COALESCE(SUM(status = 'passed'), 0),
                      COALESCE(SUM(status = 'failed'), 0), AVG(duration_ms)
               FROM runs"""
        ).fetchone()
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "success_rate": round(100 * passed / total, 2) if total else 0.0,
        "average_duration_ms": round(average_ms, 2) if average_ms is not None else 0.0,
    }
