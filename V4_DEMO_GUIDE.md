# V4 end-to-end synthetic business demo

From the repository root:

```bash
python -m business_v4.demo --output v4-demo-output
```

The demo creates three synthetic orders in a local SQLite database, processes them using the bounded worker, then generates a static dashboard at `v4-demo-output/dashboard/index.html`. Run it a second time to demonstrate idempotency: previously completed orders are not processed again.

The integration tests also exercise two concurrent workers using separate SQLite connections. This demo does not connect to real order systems, send emails or move money. It is a portfolio demonstration, not production software.
