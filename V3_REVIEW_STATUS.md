# V3 review status

This branch is reserved for the V3 hardening candidate. The complete V3 source changes have **not yet been uploaded**. Do not merge this branch into `main`.

Local checks on 2026-11-11: `python -m compileall -q automation tests` succeeded and `python -m pytest -q --ignore=tests/test_browser.py` reported 34 passed. Browser tests were not rerun in this check. Ruff and pip-audit have not yet been executed. Previous local browser results are not GitHub Actions results.

Pending: transfer reviewed V3 source files, pin GitHub Actions to verified commit SHAs, run Ruff and pip-audit, then verify GitHub Actions on this branch before considering a pull request.
