"""Capture a single final outcome per pytest item including teardown failures."""
import json
from pathlib import Path
import pytest
from automation.history import record_run, summarize

REPORT_DIR = Path("test-results")
DB = REPORT_DIR / "browser-runs.sqlite3"
_OUTCOMES = {}

@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    REPORT_DIR.mkdir(exist_ok=True)
    if DB.exists():
        DB.unlink()
    _OUTCOMES.clear()
    summary = REPORT_DIR / "summary.json"
    if summary.exists():
        summary.unlink()

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report):
    if report.when not in ("setup", "call", "teardown"):
        return
    node = report.nodeid
    state = _OUTCOMES.setdefault(node, {"status": "skipped", "duration_ms": 0, "error": None, "failed": False, "passed": False})
    state["duration_ms"] += max(0, round(report.duration * 1000))
    if report.failed:
        state["failed"] = True
        state["error"] = (state["error"] or "") + str(report.longrepr)[:2000]
    elif report.when == "call" and report.passed:
        state["passed"] = True


def pytest_sessionfinish(session, exitstatus):
    for node, state in _OUTCOMES.items():
        status = "failed" if state["failed"] else "passed" if state["passed"] else "skipped"
        record_run(DB, node, status, state["duration_ms"], state["error"] if status == "failed" else None)
    stats = summarize(DB)
    output = {"schema_version": 2, "pytest_exit_code": int(exitstatus), **stats}
    (REPORT_DIR / "summary.json").write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
