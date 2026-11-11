# V4 batch worker

The worker processes **synthetic** orders in a local SQLite database. It never contacts a payment processor or external customer system.

Run from the repository root after creating demo orders through the API or `business_v4.orders.create_order`:

```bash
python -m business_v4.worker --db v4_orders.sqlite3 --max-jobs 100
```

A batch ends when no pending orders remain or the configured job limit is reached. A second invocation resumes remaining pending orders from the database. Each order transition is committed in a SQLite transaction. `--simulate-failures` is a test-only switch to exercise retry exhaustion.

**Limitations:** this is a bounded synchronous batch worker, not yet a continuously running scheduler or distributed task queue. The example processing is synthetic; no external side effects are performed. A production integration would need explicit idempotency across external services, backoff, dead-letter handling, operational metrics and security hardening.
