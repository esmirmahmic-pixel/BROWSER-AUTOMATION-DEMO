# V4 Business Automation Platform — development branch

Goal: demonstrate reliable processing of **synthetic** company orders. This is a portfolio exercise, not a production service.

## Phase 1 (implemented)
- SQLite order ledger with persistent statuses.
- Idempotent order creation; conflicting duplicate IDs rejected.
- Atomic transaction for processing the next pending order.
- Bounded retries and terminal failed status.
- Input validation and automated unit tests.

## Next phases (not yet implemented)
1. REST API with authentication and rate limits.
2. Background worker with concurrency and recovery tests.
3. Playwright integration against a local demo order portal.
4. Dashboard for order throughput, failures and latency.
5. Security review, operational documentation and CI evidence.

Do not describe the project as production-ready or claim these future phases are already implemented.
