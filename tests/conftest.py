"""Capture actual pytest outcomes into a SQLite database and JSON report."""
import json
from pathlib import Path
import pytest

from automation.history import record_run, summarize

REPORT_DIR = Path("test-results")
DB = REPORT_DIR / "browser-runs.sqlite3"


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    REPORT_DIR.mkdir(exist_ok=True)
    if DB.exists():
        DB.unlink()


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report):
    # Record one outcome per test. A setup failure is also a failed test.
    if report.when not in ("setup", "call"):
        return
    if report.when == "setup" and report.passed:
        return
    if report.when == "call" and report.skipped:
        return
    status = "passed" if report.passed else "failed"
    error = str(report.longrepr)[:2000] if report.failed else None
    record_run(DB, report.nodeid, status, max(0, round(report.duration * 1000)), error)


def pytest_sessionfinish(session, exitstatus):
    stats = summarize(DB)
    output = {"schema_version": 1, "pytest_exit_code": int(exitstatus), **stats}
    (REPORT_DIR / "summary.json").write_text(
        json.dumps(output, indent=2, sort_keys=True), encoding="utf-8"
    )
