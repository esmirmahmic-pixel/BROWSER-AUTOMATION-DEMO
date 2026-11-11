"""Build a static, escaped dashboard from a local synthetic-orders SQLite DB."""
import argparse
import html
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from business_v4.orders import connect, summary


def render(data: dict, rows: list[dict], generated_at: str | None = None) -> str:
    cards = "".join(
        f'<article class="card"><span>{html.escape(label)}</span><strong>{int(data[key])}</strong></article>'
        for key, label in [
            ("total", "Total orders"), ("pending", "Pending"),
            ("completed", "Completed"), ("failed", "Failed"),
        ]
    )
    table_rows = "".join(
        "<tr>" + "".join(
            f"<td data-label=\"{label}\">{html.escape(str(row[key]), quote=True)}</td>"
            for key, label in (("id", "Order ID"), ("customer", "Customer"), ("amount_cents", "Amount (cents)"), ("status", "Status"), ("attempts", "Attempts"))
        ) + "</tr>"
        for row in rows
    )
    if not table_rows:
        table_rows = '<tr><td colspan="5">No demo orders yet</td></tr>'
    total_cents = sum(int(row["amount_cents"]) for row in rows if row["status"] == "completed")
    generated = html.escape(generated_at or "Not supplied", quote=True)
    return """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>V4.1 Business Automation | Demo Dashboard</title>
<style>
:root{color-scheme:dark;font-family:system-ui,sans-serif;background:#0c1423;color:#e7edf7}
body{max-width:1050px;margin:0 auto;padding:28px 16px}
h1{font-size:clamp(1.5rem,4vw,2.4rem)}p{color:#aebed3;line-height:1.5}
.kicker{font-size:.85rem;letter-spacing:.08em;text-transform:uppercase;color:#9bc8fa}
.meta{background:#142237;border:1px solid #30445e;border-radius:12px;padding:12px 16px;margin:16px 0}
.meta strong{color:#e7edf7}.meta time{overflow-wrap:anywhere}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin:24px 0}
.card{background:#19283c;padding:22px;border:1px solid #30445e;border-radius:14px}
.card span{display:block;color:#b8c9db}.card strong{display:block;font-size:2.3rem;margin-top:10px}
section{background:#19283c;border-radius:14px;padding:14px;overflow-x:auto}
@media(max-width:600px){body{padding:18px 12px}.grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin:16px 0}.card{padding:14px;border-radius:12px}.card strong{font-size:1.8rem}.card span{font-size:.85rem}section{padding:14px}table,tbody,tr,td{display:block;width:100%;box-sizing:border-box}thead{display:none}tr{padding:10px 0;border-bottom:1px solid #40516a}td{display:grid;grid-template-columns:minmax(100px,40%) minmax(0,1fr);gap:8px;padding:7px 0;border:0;overflow-wrap:anywhere}td:before{content:attr(data-label);color:#b8c9db;font-weight:600}td[colspan]{display:block}td[colspan]:before{display:none}}

table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:12px;border-bottom:1px solid #30445e}
small{color:#aebed3}
</style></head><body><div class="kicker">Portfolio demonstration · V4.1</div><h1>Business Automation V4.1</h1>
<p>Local demonstration dashboard · synthetic orders only · snapshot, not live data</p>
<div class="grid">""" + cards + """</div>
<div class="meta"><strong>Completed order value:</strong> """ + f"{total_cents / 100:,.2f}" + """ demo currency units
<p>Last report generated (UTC): <time>""" + generated + """</time></p></div>
<section><h2>Recent orders</h2><table><thead><tr>
<th>ID</th><th>Customer</th><th>Amount (cents)</th><th>Status</th><th>Attempts</th>
</tr></thead><tbody>""" + table_rows + """</tbody></table></section>
<p><small>Generated from a local SQLite snapshot. No customer or payment system is connected.</small></p>
</body></html>"""


def build(db_path: str | Path, output_dir: str | Path) -> dict:
    with connect(db_path) as db:
        data = summary(db)
        rows = [
            dict(row) for row in db.execute(
                "SELECT id,customer,amount_cents,status,attempts "
                "FROM orders ORDER BY created_at DESC,id DESC LIMIT 50"
            )
        ]
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()
    report = {"schema_version": 1, "generated_at": generated_at,
              "demo_only": True, "counts": data, "recent_orders": rows}
    for filename, content in [
        ("index.html", render(data, rows, generated_at)),
        ("summary.json", json.dumps(report, ensure_ascii=False, indent=2)),
    ]:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output,
                                         prefix=".v4-", delete=False) as temp:
            temp.write(content)
            temp_path = Path(temp.name)
        os.replace(temp_path, output / filename)
    return report


def main():
    parser = argparse.ArgumentParser(description="Generate V4 demo order dashboard")
    parser.add_argument("--db", default="v4_orders.sqlite3")
    parser.add_argument("--output", default="v4-dashboard")
    args = parser.parse_args()
    report = build(args.db, args.output)
    print(json.dumps(report["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
