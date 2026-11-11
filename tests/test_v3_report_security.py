"""Regression tests for report integrity and publish safety."""
import pytest
from automation.build_dashboard import validate

GOOD = {"schema_version": 2, "total": 3, "passed": 3, "failed": 0, "skipped": 0, "pytest_exit_code": 0}

@pytest.mark.parametrize("change", [
    {"skipped": 1, "passed": 2},
    {"failed": 1, "passed": 2},
    {"pytest_exit_code": 1},
    {"total": 4},
    {"passed": True},
    {"schema_version": 99},
    {"total": 0, "passed": 0},
])
def test_reject_non_publishable_report(change):
    with pytest.raises(ValueError):
        validate({**GOOD, **change})

def test_accept_complete_successful_report():
    validate(GOOD)
