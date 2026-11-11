"""V4 business workflow tests: idempotency, validation, retry and persistence."""
import pytest
from business_v4.orders import connect, create_order, process_next, summary


@pytest.fixture
def db(tmp_path):
    connection = connect(tmp_path / "orders.sqlite3")
    yield connection
    connection.close()


def test_create_and_complete(db):
    order = create_order(db, "A-001", "Demo Customer", 2500)
    assert order["status"] == "pending"
    result = process_next(db)
    assert result["status"] == "completed"
    assert summary(db) == {"total": 1, "pending": 0, "completed": 1, "failed": 0}


def test_idempotent_order(db):
    first = create_order(db, "A-001", "Demo", 100)
    second = create_order(db, "A-001", "Demo", 100)
    assert first == second
    assert summary(db)["total"] == 1


def test_idempotency_conflict(db):
    create_order(db, "A-001", "Demo", 100)
    with pytest.raises(ValueError):
        create_order(db, "A-001", "Demo", 200)


@pytest.mark.parametrize("order_id,customer,amount", [
    ("", "Demo", 100), ("A", "", 100), ("A", "Demo", 0),
    ("A", "Demo", -1), ("A", "Demo", True), ("A", "Demo", 100_000_001),
])
def test_invalid_orders(db, order_id, customer, amount):
    with pytest.raises(ValueError):
        create_order(db, order_id, customer, amount)


def test_retry_then_success(db):
    create_order(db, "A", "Demo", 100)
    assert process_next(db, simulate_failure=True)["status"] == "pending"
    assert process_next(db)["status"] == "completed"
    assert process_next(db) is None


def test_retry_exhaustion(db):
    create_order(db, "A", "Demo", 100)
    for _ in range(3):
        result = process_next(db, simulate_failure=True)
    assert result["status"] == "failed"
    assert result["attempts"] == 3
    assert process_next(db) is None


def test_persists_after_reconnect(tmp_path):
    path = tmp_path / "persist.db"
    with connect(path) as db:
        create_order(db, "A", "Demo", 100)
    with connect(path) as db:
        assert summary(db)["pending"] == 1
