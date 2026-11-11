# V4 public demo — deployment plan

**Current state:** The development branch builds a synthetic V4 dashboard preview as part of the existing GitHub Actions workflow. It is **not published** until the branch is reviewed and merged into `main` after successful checks.

## Intended public URL after approved merge

https://esmirmahmic-pixel.github.io/BROWSER-AUTOMATION-DEMO/v4/

The existing V3 test dashboard remains at the root URL.

## What visitors will see

A static HTML dashboard generated from exactly three synthetic example orders. It displays total, pending, completed and failed counts plus an example order table. No token, SQLite database or real customer information is published.

## How publishing works

1. GitHub Actions runs the full configured test suite.
2. Only after successful verification, CI executes `python -m business_v4.demo`.
3. CI checks the generated `summary.json` contains exactly three synthetic `DEMO-` orders and all three are completed.
4. The preview is copied into `test-results/dashboard/v4/` and uploaded alongside the existing V3 dashboard preview.
5. On `main` only, the publish job verifies both V3 and V4 bundles before GitHub Pages deployment.

## Limits

The public page is a **static demonstration snapshot**. It cannot accept orders or invoke the localhost API. No server-side worker is hosted on GitHub Pages. Do not represent it as a live business system.

## Release checklist

- [ ] CI successful on latest V4 head
- [ ] Review the V4 pull request changes and preview artifact
- [ ] Confirm no secrets or personal information in the published files
- [ ] Explicitly approve merge into `main`
- [ ] Verify the public /v4/ URL after deployment
