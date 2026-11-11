"""SQLite history with one final outcome per pytest node id."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK(status IN ('passed', 'failed', 'skipped')),
    duration_ms INTEGER NOT NULL CHECK(duration_ms >= 0),
    error TEXT,
    created_at TEXT NOT NULL
)"""


def record_run(db_path: str | Path, task: str, status: str, duration_ms: int,
               error: str | None = None) -> int:
    if status not in {"passed", "failed", "skipped"}:
        raise ValueError("invalid status")
    if not isinstance(task, str) or not task.strip() or not isinstance(duration_ms, int) or duration_ms < 0:
        raise ValueError("task must be nonempty and duration_ms nonnegative integer")
    if status != "failed" and error:
        raise ValueError("only failed runs may have an error")
    with sqlite3.connect(db_path) as connection:
        connection.execute(SCHEMA)
        cursor = connection.execute("""INSERT INTO runs(task,status,duration_ms,error,created_at)
            VALUES(?,?,?,?,?) ON CONFLICT(task) DO UPDATE SET
            status=excluded.status,duration_ms=excluded.duration_ms,
            error=excluded.error,created_at=excluded.created_at""",
            (task, status, duration_ms, error, datetime.now(timezone.utc).isoformat()))
        return int(cursor.lastrowid or connection.execute('SELECT id FROM runs WHERE task=?',(task,)).fetchone()[0])


def summarize(db_path: str | Path) -> dict:
    with sqlite3.connect(db_path) as connection:
        connection.execute(SCHEMA)
        total, passed, failed, skipped, average_ms = connection.execute("""SELECT COUNT(*),
            COALESCE(SUM(status='passed'),0), COALESCE(SUM(status='failed'),0),
            COALESCE(SUM(status='skipped'),0), AVG(duration_ms) FROM runs""").fetchone()
    completed = passed + failed
    return {"total": total, "passed": passed, "failed": failed, "skipped": skipped,
            "success_rate": round(100 * passed / completed, 2) if completed else 0.0,
            "average_duration_ms": round(average_ms, 2) if average_ms is not None else 0.0}
