# Business Automation Platform V4 — Portfolio Case Study

**Status:** Tested development prototype, not production software.  
**Repository:** [BROWSER-AUTOMATION-DEMO](https://github.com/esmirmahmic-pixel/BROWSER-AUTOMATION-DEMO)  
**Development review:** [V4 pull request #2](https://github.com/esmirmahmic-pixel/BROWSER-AUTOMATION-DEMO/pull/2)

## Business problem

A small business receives orders that need validation, durable storage, repeatable processing and a clear status report. Manual processing risks duplicate entries and inconsistent results.

## Demonstrated solution

This Python prototype implements a **synthetic order workflow**:

1. Accept a demo order using a local HTTP API protected by a bearer token.
2. Validate the payload and store the order in SQLite.
3. Prevent duplicates using an order ID; reject the same ID with conflicting details.
4. Process pending orders using a bounded worker, with configurable retry limits.
5. Generate a static HTML and JSON dashboard summarizing order status.
6. Verify behavior using automated tests and GitHub Actions.

The demo script `python -m business_v4.demo --output v4-demo-output` runs intake, processing and reporting end to end with three sample orders.

## Technical design

| Component | Purpose | Implementation |
| --- | --- | --- |
| `business_v4/orders.py` | Order ledger, idempotency, state changes | Python, SQLite transactions |
| `business_v4/api.py` | Local order intake and query API | Python standard-library HTTP server |
| `business_v4/worker.py` | Bounded processing, retry attempts | Python, SQLite |
| `business_v4/dashboard.py` | Snapshot reporting | Escaped HTML, JSON |
| `business_v4/demo.py` | Reproducible example | Synthetic data |
| `tests/test_business_v4_*.py` | Unit, HTTP, security and integration checks | pytest |
| `.github/workflows/browser-tests.yml` | CI validation | GitHub Actions |

## Engineering decisions

- **SQLite transactions** preserve order status changes and avoid simultaneous workers selecting the same pending item.
- **Idempotent order intake** ensures repeated requests with the same order ID and identical payload do not create duplicates.
- **Bounded retries** prevent unlimited processing loops; exhausted jobs enter a failed state.
- **Local-only API binding** keeps the demo service on `127.0.0.1`. Tokens are supplied via environment variables, not committed to source.
- **Escaped HTML output** reduces the risk of injecting order field content into dashboard markup.
- **GitHub CI** validates Python syntax, linting, dependency audit and pytest before publication of the existing V3 dashboard.

## Verification evidence

GitHub Actions run [43068531705](https://github.com/esmirmahmic-pixel/BROWSER-AUTOMATION-DEMO/actions/runs/43068531705) completed successfully for V4 commit `e967ebb8874d0f5a6c66942cae45440d84264188`. Its test job passed. GitHub Pages publishing was skipped for the development branch, as intended.

A passing CI run confirms the configured checks passed for that commit. It is **not** proof of production readiness, real-customer performance, uptime, or security certification.

## Scope and limitations

- **No real orders, payments, emails or external customer systems.** All example records are synthetic.
- The API is **localhost-only**, not an internet-facing production service.
- The worker runs in bounded batches, not as a continuously managed service.
- Dashboard is a **static snapshot**, not a live operational console.
- There is no real payment integration, multi-user authorization, distributed queue or deployment SLA.
- This is a portfolio demonstration of engineering techniques, not a claim of any formal job seniority.

## Potential next steps

- Add a configurable real-world adapter against a sandbox API.
- Add structured logging, metrics, backoff and failure recovery.
- Implement stronger service authentication, rate limiting and deployment protections.
- Measure throughput and latency under repeatable load tests.
- Produce a short narrated demonstration and architecture walkthrough.

## How to reproduce

From the repository root, install dependencies in a Python 3.11 virtual environment and run:

```bash
python -m pytest -q
python -m business_v4.demo --output v4-demo-output
```

Then open `v4-demo-output/dashboard/index.html` locally. The test command includes the broader repository's browser tests and may require Playwright Chromium; see the existing project setup and CI workflow.
