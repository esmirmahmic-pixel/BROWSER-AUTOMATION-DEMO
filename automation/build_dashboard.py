"""Build a static dashboard bundle from real pytest results only."""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "test-results" / "summary.json"
DEST = ROOT / "test-results" / "dashboard"


def main():
    if not SOURCE.is_file():
        raise SystemExit("No pytest summary found; refusing to publish placeholder statistics")
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    for key in ("total", "passed", "failed", "pytest_exit_code"):
        if not isinstance(data.get(key), int) or isinstance(data[key], bool):
            raise SystemExit(f"Invalid CI summary: {key}")
    if data["total"] < 0 or data["passed"] < 0 or data["failed"] < 0:
        raise SystemExit("Invalid negative test counts")
    if data["passed"] + data["failed"] != data["total"]:
        raise SystemExit("Inconsistent test counts")
    DEST.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "dashboard" / "index.html", DEST / "index.html")
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    (DEST / "summary.json").write_text(
        json.dumps(data, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(f"Dashboard bundle ready: {DEST}")


if __name__ == "__main__":
    main()
