"""Regression tests for JSON/JUnit consistency before publishing."""
import json
import xml.etree.ElementTree as ET
import pytest
from automation.verify_results import verify

def make_reports(tmp_path, *, tests=2, failures=0, errors=0, skipped=0, passed=2):
    summary=tmp_path/"summary.json"
    junit=tmp_path/"results.xml"
    summary.write_text(json.dumps({"schema_version":2,"pytest_exit_code":0,
        "total":2,"passed":passed,"failed":0,"skipped":0}),encoding="utf-8")
    root=ET.Element("testsuites")
    ET.SubElement(root,"testsuite",tests=str(tests),failures=str(failures),
        errors=str(errors),skipped=str(skipped))
    ET.ElementTree(root).write(junit,encoding="unicode")
    return summary,junit

def test_matching_reports_are_accepted(tmp_path):
    summary,junit=make_reports(tmp_path)
    assert verify(summary,junit)["tests"]==2

@pytest.mark.parametrize("change",[
    {"tests":3},{"failures":1},{"errors":1},{"skipped":1},{"passed":1}
])
def test_mismatch_or_non_success_rejected(tmp_path,change):
    passed=change.pop("passed",2) if "passed" in change else 2
    summary,junit=make_reports(tmp_path,passed=passed,**change)
    with pytest.raises(ValueError):
        verify(summary,junit)
