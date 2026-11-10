# Browser Automation Demo

[**View the public test dashboard**](https://esmirmahmic-pixel.github.io/BROWSER-AUTOMATION-DEMO/) · [**View GitHub Actions runs**](https://github.com/esmirmahmic-pixel/BROWSER-AUTOMATION-DEMO/actions) · [**Verified passing run #22**](https://github.com/esmirmahmic-pixel/BROWSER-AUTOMATION-DEMO/actions/runs/42853468200)

A small, reproducible **Python + Playwright** portfolio demonstration of browser automation, automated testing, bounded retries, SQLite test history, and evidence-based reporting.

> **Portfolio demonstration, not a production automation service.** The dashboard displays the latest *published* CI result; it does not monitor a live service.

## Verified demonstration

The publicly published dashboard was visually checked on **10 November 2026** and displayed **15 tests, 15 passed, 0 failed (100% for that run)**. These numbers are a snapshot of executed tests, not a claim of perfect software reliability. For current results, open the dashboard and check the timestamp. The linked [GitHub Actions run #22](https://github.com/esmirmahmic-pixel/BROWSER-AUTOMATION-DEMO/actions/runs/42853468200) is an independently inspectable successful run.

## What this project demonstrates

| Area | Demonstration |
| --- | --- |
| Browser automation | Playwright driving Chromium against a controlled local HTML form |
| Input validation | Successful submission and required-field behavior |
| Resilience | Limited retries for simulated transient timeouts, without retrying unrelated exceptions |
| Test history | SQLite records test outcomes, including failures |
| Reporting | Pytest-generated JSON/XML results and a static dashboard built from actual test data |
| CI/CD | GitHub Actions runs tests on Ubuntu 24.04 and publishes a dashboard only after a successful test job and report verification |

## Try it locally

Requires **Python 3.11**, a supported operating system, and Chromium dependencies.

```bash
python -m pip install -r requirements.txt
python -m playwright install --with-deps chromium
python -m pytest -v -ra --junitxml=test-results/results.xml
python -m automation.build_dashboard
```

Open `test-results/dashboard/index.html` using a local web server so its `summary.json` can be fetched:

```bash
cd test-results/dashboard
python -m http.server 8000
```

Then visit `http://localhost:8000/`.

The test outputs include `test-results/summary.json`, `test-results/results.xml`, and `test-results/browser-runs.sqlite3`. CI additionally uploads downloadable artifacts.

## Project structure

- `tests/` — browser tests and unit tests for reporting, retries, and history
- `automation/retry.py` — bounded retry utility
- `automation/history.py` — SQLite run history
- `automation/build_dashboard.py` — builds a report bundle from real test results
- `demo/form.html` — controlled test form
- `dashboard/index.html` — static dashboard interface
- `.github/workflows/browser-tests.yml` — CI testing and Pages deployment

## Boundaries

This demo does **not** log into third-party sites, scrape private information, use customer credentials, or place real orders. It is separate from any trading software and from the PythonAnywhere site. It should not be described as commercial production experience.

## Next improvements

Expand realistic browser scenarios, add accessibility checks, and document test coverage and failure diagnostics. Changes should continue to be validated by CI before publishing.
