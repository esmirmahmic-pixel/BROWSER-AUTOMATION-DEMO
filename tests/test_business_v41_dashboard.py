"""Regression checks for the V4.1 mobile portfolio dashboard."""
from business_v4.dashboard import render


def test_mobile_cards_and_order_labels():
    page = render(
        {"total": 1, "pending": 0, "completed": 1, "failed": 0},
        [{"id": "DEMO-001", "customer": "Example", "amount_cents": 1299,
          "status": "completed", "attempts": 1}],
        "2026-11-11T18:00:00+00:00",
    )
    assert "@media(max-width:600px)" in page
    assert 'data-label="Status"' in page
    assert 'data-label="Order ID"' in page
    assert "12.99" in page
    assert "2026-11-11T18:00:00+00:00" in page


def test_generated_timestamp_is_escaped():
    page = render(
        {"total": 0, "pending": 0, "completed": 0, "failed": 0},
        [],
        "<script>alert(1)</script>",
    )
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page
