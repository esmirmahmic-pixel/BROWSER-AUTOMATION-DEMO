"""Fail closed when pytest JSON and JUnit XML disagree."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path


def verify(summary_path: Path, junit_path: Path) -> dict:
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON report must be an object")
    root = ET.parse(junit_path).getroot()
    if root.tag == "testsuite":
        suites = [root]
    elif root.tag == "testsuites":
        suites = list(root.findall("testsuite"))
    else:
        raise ValueError("Invalid JUnit root element")
    if not suites:
        raise ValueError("JUnit XML contains no test suites")

    keys = ("tests", "failures", "errors", "skipped")
    totals = {key: 0 for key in keys}
    for suite in suites:
        for key in keys:
            value = int(suite.get(key, "-1"))
            if value < 0:
                raise ValueError(f"Invalid JUnit {key} count")
            totals[key] += value

    failed = totals["failures"] + totals["errors"]
    passed = totals["tests"] - failed - totals["skipped"]
    if passed < 0:
        raise ValueError("JUnit counts are inconsistent")
    expected = {
        "schema_version": 2,
        "pytest_exit_code": 0,
        "total": totals["tests"],
        "passed": passed,
        "failed": failed,
        "skipped": totals["skipped"],
    }
    if any(type(data.get(key)) is not int or data[key] != value for key, value in expected.items()):
        raise ValueError(f"JSON/JUnit mismatch: {totals}")
    if totals["tests"] <= 0 or failed or totals["skipped"]:
        raise ValueError("Only complete, successful runs can be published")
    return totals


if __name__ == "__main__":
    print("Verified JSON/JUnit agreement:", verify(
        Path("test-results/summary.json"), Path("test-results/results.xml")))
