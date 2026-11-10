# Browser Automation Demo

An experimental Python/Playwright portfolio project demonstrating browser automation, repeatable testing, error tracking, and reporting. **Not a production service.**

## Features
- Controlled local HTML form (no third-party scraping or credentials)
- Chromium automation: successful submission and required-field validation
- SQLite-backed pytest run history, including failed test details
- Bounded retries for temporary timeouts, with no retry on unrelated errors
- JSON summary of executed tests
- GitHub Actions execution with downloadable test artifacts

## Run locally

Requires Python 3.11 and a supported environment for Chromium.

```bash
python -m pip install -r requirements.txt
python -m playwright install --with-deps chromium
python -m pytest -v -ra
```

After running, inspect `test-results/summary.json`, `test-results/browser-runs.sqlite3`, and `test-results/results.xml` (the XML file is produced by CI, or locally when using `--junitxml=test-results/results.xml`).

## CI evidence

Open the **Actions** tab and select the latest **Browser automation tests** run. Its **browser-test-results** artifact contains the actual test reports, including failures. A successful code commit does **not** mean the CI tests passed; verify the run conclusion.

## Scope and security

No passwords, API tokens, or real customer data are used. This repository is independent of PROP TRADER AI and the PythonAnywhere trading dashboard. The public demo has **not** been deployed to PythonAnywhere.

## Next milestones

- Verify the retry demonstration in GitHub Actions
- Simple dashboard reading JSON results
- Secure, separate deployment plan for the PythonAnywhere site
