import asyncio
import contextlib
import functools
import logging
import random
import time
from collections.abc import AsyncGenerator, Callable
from typing import ParamSpec, TypeVar

import aiohttp
from botocore.exceptions import ClientError
from litellm import RouterRateLimitError

from sifts.io.db.types import AnalysisFacet

TVar = TypeVar("TVar")

P = ParamSpec("P")

LOGGER = logging.getLogger(__name__)


def _get_retry_sleep_info(  # noqa: PLR0911
    exc: Exception,
    default_sleep_seconds: float,
) -> tuple[bool, float]:
    if isinstance(exc, RouterRateLimitError):
        return False, exc.cooldown_time

    if isinstance(exc, ClientError):
        meta = getattr(exc, "response", {})
        status_code = meta.get("OriginalStatusCode") or meta.get(
            "ResponseMetadata",
            {},
        ).get("HTTPStatusCode")
        if status_code in (424, 429, 0):
            return True, default_sleep_seconds
        return False, default_sleep_seconds

    if isinstance(exc, aiohttp.ClientResponseError):
        # Respect Retry-After for rate limits
        if exc.status == 429:  # noqa: PLR2004
            return False, float(
                (exc.headers.get("Retry-After", default_sleep_seconds) if exc.headers else None)
                or default_sleep_seconds,
            )
        # Transient network/server errors
        if exc.status in (400, 408, 425, 500, 502, 503, 504):
            return False, default_sleep_seconds

    # Handle generic aiohttp client/network issues and timeouts
    if isinstance(
        exc,
        (aiohttp.ClientConnectorError, aiohttp.ServerTimeoutError, aiohttp.ClientOSError),
    ):
        return False, default_sleep_seconds
    return False, default_sleep_seconds


def retry_on_exceptions(
    *,
    exceptions: tuple[type[Exception], ...],
    max_attempts: int = 5,
    sleep_seconds: float = 5,
) -> Callable[[Callable[P, TVar]], Callable[P, TVar]]:
    def decorator(
        func: Callable[P, TVar],
    ) -> Callable[P, TVar]:
        retry_delay = sleep_seconds
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def wrapper(*args: P.args, **kwargs: P.kwargs) -> TVar:
                count_attempts = 0
                while count_attempts < max_attempts:
                    count_attempts += 1
                    try:
                        return await func(*args, **kwargs)  # type: ignore  # noqa: PGH003
                    except exceptions as exc:
                        should_decrement, base_sleep = _get_retry_sleep_info(
                            exc,
                            retry_delay,
                        )
                        if should_decrement:
                            count_attempts -= 1
                        # Exponential backoff with jitter
                        backoff = base_sleep * (2 ** max(count_attempts - 1, 0))
                        jitter = random.uniform(0, base_sleep)  # noqa: S311
                        await asyncio.sleep(min(backoff + jitter, 60.0))
                    except Exception:
                        LOGGER.exception(
                            "Error calling %s, unhandled exception",
                            func.__name__,
                            stack_info=True,
                        )
                        raise
                return await func(*args, **kwargs)  # type: ignore  # noqa: PGH003

            return wrapper  # type: ignore  # noqa: PGH003

        @functools.wraps(func)
        def wrapper1(*args: P.args, **kwargs: P.kwargs) -> TVar:
            for _ in range(max_attempts - 1):
                with contextlib.suppress(*exceptions):
                    return func(*args, **kwargs)
                time.sleep(sleep_seconds)
            return func(*args, **kwargs)

        return wrapper1

    return decorator


async def merge_async_generators_concurrent(
    generators: list[AsyncGenerator[AnalysisFacet, None]],
) -> AsyncGenerator[AnalysisFacet, None]:
    """Merge multiple async generators and process them concurrently."""
    if not generators:
        return

    # Track completion with a simple counter
    pending = len(generators)
    queue: asyncio.Queue[AnalysisFacet | Exception] = asyncio.Queue()

    async def process_generator(generator: AsyncGenerator[AnalysisFacet, None]) -> None:
        nonlocal pending
        try:
            async for item in generator:
                await queue.put(item)
        except Exception as e:  # noqa: BLE001
            await queue.put(e)  # Just pass the exception directly
        finally:
            pending -= 1

    # Start all generator tasks
    for generator in generators:
        asyncio.create_task(process_generator(generator))  # noqa: RUF006

    # Process results until all generators are done and queue is empty
    while pending > 0 or not queue.empty():
        try:
            # Use a shorter timeout and simpler waiting logic
            item = await asyncio.wait_for(queue.get(), 0.05)
            if isinstance(item, Exception):
                raise item  # Re-raise any exceptions from generators
            yield item
        except TimeoutError:
            # Just continue the loop - no need for additional checks here
            pass
