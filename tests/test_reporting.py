import json
from pathlib import Path
from automation.history import record_run, summarize

def test_summary_can_be_exported_as_json(tmp_path):
    db = tmp_path / "results.sqlite3"
    record_run(db, "test_login", "passed", 120)
    record_run(db, "test_timeout", "failed", 80, "Timeout")
    report = {"schema_version": 1, **summarize(db)}
    target = tmp_path / "summary.json"
    target.write_text(json.dumps(report), encoding="utf-8")
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded["total"] == 2
    assert loaded["success_rate"] == 50.0
    assert loaded["failed"] == 1
