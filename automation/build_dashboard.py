"""Build a dashboard only from consistent, successful pytest reports."""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "test-results" / "summary.json"
DEST = ROOT / "test-results" / "dashboard"

def validate(data: dict) -> None:
    if not isinstance(data, dict):
        raise ValueError("report must be an object")
    for key in ("total", "passed", "failed", "skipped", "pytest_exit_code"):
        if type(data.get(key)) is not int:
            raise ValueError(f"invalid {key}")
    if data.get("schema_version") != 2:
        raise ValueError("unsupported report schema")
    if any(data[k] < 0 for k in ("total", "passed", "failed", "skipped")):
        raise ValueError("negative test count")
    if data["total"] <= 0 or data["total"] != data["passed"] + data["failed"] + data["skipped"]:
        raise ValueError("inconsistent test counts")
    if data["pytest_exit_code"] != 0 or data["failed"] != 0 or data["skipped"] != 0:
        raise ValueError("cannot publish unsuccessful test run")

def main():
    if not SOURCE.is_file():
        raise SystemExit("No pytest summary; refusing to publish")
    try:
        data = json.loads(SOURCE.read_text(encoding="utf-8"))
        validate(data)
    except (ValueError, OSError) as exc:
        raise SystemExit(f"Invalid pytest summary: {exc}") from exc
    DEST.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "dashboard" / "index.html", DEST / "index.html")
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    (DEST / "summary.json").write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Verified dashboard bundle: {DEST}")

if __name__ == "__main__":
    main()
