"""Retry selected transient failures without retrying unrelated errors."""
import time
from collections.abc import Callable
from typing import TypeVar
T = TypeVar("T")
def retry(action: Callable[[], T], *, attempts: int = 3, delay_seconds: float = 0.0,
          retry_on: tuple[type[Exception], ...] = (TimeoutError,),
          sleep: Callable[[float], None] = time.sleep) -> T:
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    if delay_seconds < 0:
        raise ValueError("delay_seconds must not be negative")
    if not retry_on or not all(isinstance(t, type) and issubclass(t, Exception) for t in retry_on):
        raise ValueError("retry_on must contain exception classes")
    for attempt in range(attempts):
        try:
            return action()
        except retry_on:
            if attempt == attempts - 1:
                raise
            sleep(delay_seconds)
    raise AssertionError("unreachable")
