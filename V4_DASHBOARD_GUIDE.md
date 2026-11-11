# V4 static business dashboard

Generate a local snapshot from the same synthetic-order SQLite database used by the API and worker:

```bash
python -m business_v4.dashboard --db v4_orders.sqlite3 --output v4-dashboard
```

Open `v4-dashboard/index.html` in a browser. The accompanying `summary.json` contains the same counts and up to 50 recent synthetic orders.

**Important:** this is a generated **snapshot**, not a live dashboard. It is not deployed to GitHub Pages; the existing V3 browser-test dashboard remains unchanged. The HTML escapes order fields and includes a restrictive Content Security Policy. Do not use real personal/customer information in this demo.
