# V4 local REST API (demo only)

The V4 API is intentionally bound to **127.0.0.1**. It uses a bearer token, synthetic orders and SQLite. Do not expose this server directly to the internet: it lacks TLS termination, rate limiting, robust observability and production authentication.

Start from the repository root:

```bash
export V4_API_TOKEN="replace-with-a-long-random-local-demo-token"
python -m business_v4.api
```

In another terminal:

```bash
curl -H "Authorization: Bearer $V4_API_TOKEN" -H "Content-Type: application/json" -d '{"id":"demo-001","customer":"Sample Customer","amount_cents":2500}' http://127.0.0.1:8766/api/orders
curl -H "Authorization: Bearer $V4_API_TOKEN" http://127.0.0.1:8766/api/orders/summary
```

Endpoints: `POST /api/orders`, `GET /api/orders/{id}`, `GET /api/orders/summary`, `GET /health`. All require the bearer token. Processing remains a separate Python function; a background worker has **not** been added yet.
