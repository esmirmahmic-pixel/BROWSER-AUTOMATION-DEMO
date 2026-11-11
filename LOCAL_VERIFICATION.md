# V3 local verification and GitHub release gate

This file describes **separate** sources of evidence. A local test result is not proof that the current GitHub branch passes CI.

## Archived candidate
The V3 ZIP was tested locally on 2026-11-11. The latest reported non-browser subset was **34 passed**. Browser tests have passed in earlier local runs with system Chromium, but they have **not** been rerun against the current assembled GitHub branch.

## GitHub branch
Branch: `review/v3-hardening-2026-11-11`. This branch has received incremental changes and may differ from the original ZIP. No completed CI run for the current head has yet been verified.

## Release checklist
- [ ] Check out the current branch HEAD and install dependencies.
- [ ] Run `python -m compileall -q automation tests`.
- [ ] Run `python -m ruff check --select E4,E9,F automation tests`.
- [ ] Run `python -m pip_audit -r requirements.txt`.
- [ ] Install Chromium with `python -m playwright install --with-deps chromium`.
- [ ] Run `python -m pytest -v -ra --junitxml=test-results/results.xml`.
- [ ] Confirm pytest counts equal `test-results/summary.json` and the JUnit XML totals.
- [ ] Run `python -m automation.build_dashboard` and inspect the result.
- [ ] Pin GitHub Actions to verified immutable commit SHAs.
- [ ] Verify the GitHub Actions run for the **same commit** and inspect logs/artifacts.
- [ ] Obtain explicit approval before merging to `main`.

Do not publish the V3 branch as production-ready until these checks are complete.
