"""Bounded retry helper for transient browser automation failures."""
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def retry(
    action: Callable[[], T],
    *,
    attempts: int = 3,
    delay_seconds: float = 0.0,
    retry_on: tuple[type[Exception], ...] = (TimeoutError,),
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Retry only explicitly allowed exceptions; propagate the last failure."""
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    if delay_seconds < 0:
        raise ValueError("delay_seconds must not be negative")
    for attempt in range(attempts):
        try:
            return action()
        except retry_on:
            if attempt == attempts - 1:
                raise
            sleep(delay_seconds)
    raise AssertionError("unreachable")
