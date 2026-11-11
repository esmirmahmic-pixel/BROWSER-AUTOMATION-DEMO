"""Verify pytest JSON and JUnit XML agree before publishing artifacts."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path

def verify(summary_path: Path, junit_path: Path) -> dict:
    data=json.loads(summary_path.read_text(encoding="utf-8"))
    root=ET.parse(junit_path).getroot()
    suites=[root] if root.tag=="testsuite" else list(root.findall("testsuite"))
    if not suites:
        raise ValueError("JUnit XML contains no test suites")
    totals={key:sum(int(s.get(key,"0")) for s in suites) for key in ("tests","failures","errors","skipped")}
    failed=totals["failures"]+totals["errors"]
    if (data.get("schema_version")!=2 or data.get("pytest_exit_code")!=0 or
        data.get("total")!=totals["tests"] or data.get("passed")!=totals["tests"]-failed-totals["skipped"] or
        data.get("failed")!=failed or data.get("skipped")!=totals["skipped"] or
        failed!=0 or totals["skipped"]!=0 or totals["tests"]<=0):
        raise ValueError(f"JSON/JUnit test results mismatch or unsuccessful run: {totals}")
    return totals

if __name__=="__main__":
    result=verify(Path("test-results/summary.json"),Path("test-results/results.xml"))
    print("Verified JSON/JUnit agreement:",result)
