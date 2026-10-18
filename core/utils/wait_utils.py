"""Dynamic wait utilities and polling helpers for resilient test automation."""

from __future__ import annotations

import time
from typing import Callable, TypeVar, Optional
from core.utils.logger import framework_logger

T = TypeVar("T")


def poll_until(
    condition_fn: Callable[[], T],
    timeout: float = 15.0,
    interval: float = 0.5,
    error_message: str = "Condition not met within timeout",
) -> T:
    """Polls a callable until it returns a truthy value or timeout expires.

    Args:
        condition_fn: Zero-argument callable returning truthy/falsy.
        timeout: Maximum time to wait in seconds.
        interval: Polling frequency in seconds.
        error_message: Message to raise on TimeoutError.

    Returns:
        The truthy result of condition_fn.

    Raises:
        TimeoutError: If condition is not met within timeout.
    """
    start_time = time.time()
    last_exception = None

    while time.time() - start_time < timeout:
        try:
            result = condition_fn()
            if result:
                return result
        except Exception as exc:
            last_exception = exc
        time.sleep(interval)

    msg = f"{error_message} (Timeout: {timeout}s)"
    if last_exception:
        msg += f". Last exception: {last_exception}"
    framework_logger.error(msg)
    raise TimeoutError(msg)


def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 1.5,
    allowed_exceptions: tuple = (Exception,),
):
    """Decorator to retry a flaky function call with exponential backoff."""

    def decorator(fn: Callable):
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_err = None
            for attempt in range(1, max_retries + 1):
                try:
                    return fn(*args, **kwargs)
                except allowed_exceptions as err:
                    last_err = err
                    framework_logger.warning(
                        f"Retry {attempt}/{max_retries} for {fn.__name__} after error: {err}"
                    )
                    if attempt == max_retries:
                        break
                    time.sleep(current_delay)
                    current_delay *= backoff
            framework_logger.error(f"Function {fn.__name__} failed after {max_retries} retries.")
            raise last_err

        return wrapper

    return decorator
