"""Bounded batch worker tests."""
import pytest

from business_v4.orders import connect, create_order
from business_v4.worker import run_batch


def seed(path, count):
    with connect(path) as db:
        for index in range(count):
            create_order(db, f"order-{index}", "Demo", 100)


def test_batch_processes_all(tmp_path):
    path = tmp_path / "orders.db"
    seed(path, 5)
    result = run_batch(path)
    assert result["attempts_processed"] == 5
    assert result["completed"] == 5
    assert result["pending"] == 0


def test_batch_respects_limit_and_can_resume(tmp_path):
    path = tmp_path / "orders.db"
    seed(path, 5)
    first = run_batch(path, max_jobs=2)
    assert first["completed"] == 2
    assert first["pending"] == 3
    second = run_batch(path, max_jobs=10)
    assert second["completed"] == 5
    assert second["attempts_processed"] == 3


def test_retry_exhaustion_is_bounded(tmp_path):
    path = tmp_path / "orders.db"
    seed(path, 1)
    result = run_batch(path, max_jobs=50, max_attempts=3, simulate_failures=True)
    assert result["attempts_processed"] == 3
    assert result["failed"] == 1
    assert run_batch(path)["attempts_processed"] == 0


@pytest.mark.parametrize("jobs,attempts", [(0, 3), (-1, 3), (10001, 3), (1, 0), (1, 101), (True, 3)])
def test_rejects_invalid_limits(tmp_path, jobs, attempts):
    with pytest.raises(ValueError):
        run_batch(tmp_path / "orders.db", max_jobs=jobs, max_attempts=attempts)
