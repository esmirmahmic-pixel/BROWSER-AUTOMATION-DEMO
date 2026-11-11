# V3 hardening review — isolated development branch

**Status:** In progress. Not approved for merge or deployment.

## Completed GitHub changes
- SQLite history records passed, failed, and skipped outcomes and updates each test node only once.
- Pytest hook records setup, call, and teardown outcomes, including teardown failures.
- Dashboard validation rejects inconsistent, skipped, failed, or unsuccessful pytest reports.
- Regression tests added for report integrity and hook behavior.
- CI workflow updated to run Python compilation, Ruff lint, pip-audit, tests, and strict dashboard generation.

## Local evidence
On 2026-11-11 the archived V3 candidate was extracted and tested locally with:
`python -m pytest -q --ignore=tests/test_browser.py`
Result: **34 passed in 0.24s**.

**Important:** This tests the archived local V3 candidate, not the assembled GitHub branch. Browser tests were excluded in this run.

## Outstanding before any merge
1. Compare all source and test files on this branch with the V3 candidate archive; transfer any missing updates.
2. Verify the entire assembled branch with GitHub Actions; inspect logs and artifacts.
3. Resolve any Ruff and pip-audit findings. These tools are not installed in the local environment.
4. Pin GitHub Actions `uses:` references to verified full commit SHAs.
5. Confirm test results and dashboard counts match, including skipped and teardown-failure cases.
6. Require explicit owner approval before merging to `main`.

**No merge to main has been authorized.**
