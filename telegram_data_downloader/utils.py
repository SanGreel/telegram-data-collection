import asyncio
import functools
import logging
from typing import Any, Callable, Optional, Tuple, Type, Union


logger = logging.getLogger(__name__)


def async_retry(
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]],
    base_sleep_time: float = 1.0,
    max_tries: int = 3,
) -> Callable:
    """
    Decorator for async functions to implement retry logic with exponential backoff.
    """
    if isinstance(exceptions, type):
        exceptions = (exceptions,)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Optional[Exception] = None
            for try_number in range(max_tries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if try_number == max_tries - 1:
                        raise

                    sleep_time = base_sleep_time * (2**try_number)
                    logger.error(
                        "attempt %d/%d failed with %s. Retrying in %.2f seconds...",
                        try_number + 1,
                        max_tries,
                        e.__class__.__name__,
                        sleep_time,
                    )
                    await asyncio.sleep(sleep_time)

            # This should never be reached due to the raise in the last iteration
            raise (
                last_exception
                if last_exception
                else RuntimeError("Unexpected error in retry logic")
            )

        return wrapper

    return decorator
