import pytest
from automation.retry import retry


def test_transient_timeout_recovers():
    calls = []
    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise TimeoutError("temporary delay")
        return "success"
    assert retry(flaky, attempts=3) == "success"
    assert len(calls) == 3


def test_permanent_timeout_stops_after_limit():
    calls = []
    def always_fails():
        calls.append(1)
        raise TimeoutError("still unavailable")
    with pytest.raises(TimeoutError, match="still unavailable"):
        retry(always_fails, attempts=2)
    assert len(calls) == 2


def test_unexpected_error_is_not_retried():
    calls = []
    def broken():
        calls.append(1)
        raise ValueError("invalid selector")
    with pytest.raises(ValueError, match="invalid selector"):
        retry(broken, attempts=4)
    assert len(calls) == 1


def test_delay_only_between_attempts():
    sleeps = []
    calls = []
    def flaky():
        calls.append(1)
        if len(calls) == 1:
            raise TimeoutError()
        return 42
    assert retry(flaky, attempts=2, delay_seconds=0.5, sleep=sleeps.append) == 42
    assert sleeps == [0.5]


@pytest.mark.parametrize("attempts,delay", [(0, 0), (1, -1)])
def test_invalid_configuration(attempts, delay):
    with pytest.raises(ValueError):
        retry(lambda: "ok", attempts=attempts, delay_seconds=delay)
