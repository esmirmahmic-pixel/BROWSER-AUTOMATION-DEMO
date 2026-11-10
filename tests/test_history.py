import pytest
from automation.history import record_run, summarize

def test_empty_history(tmp_path):
    assert summarize(tmp_path / "runs.sqlite3") == {
        "total": 0, "passed": 0, "failed": 0,
        "success_rate": 0.0, "average_duration_ms": 0.0,
    }

def test_history_statistics(tmp_path):
    db = tmp_path / "runs.sqlite3"
    first = record_run(db, "form_submission", "passed", 100)
    second = record_run(db, "timeout_recovery", "failed", 300, "Timed out")
    assert second > first
    assert summarize(db) == {
        "total": 2, "passed": 1, "failed": 1,
        "success_rate": 50.0, "average_duration_ms": 200.0,
    }

@pytest.mark.parametrize("status,duration,error", [
    ("unknown", 10, None),
    ("passed", -1, None),
    ("passed", 10, "unexpected"),
])
def test_reject_invalid_runs(tmp_path, status, duration, error):
    with pytest.raises(ValueError):
        record_run(tmp_path / "runs.sqlite3", "demo", status, duration, error)
