import asyncio
import logging
from collections.abc import AsyncGenerator, Coroutine, Iterable
from contextlib import suppress
from typing import Any, TypeVar, cast

T = TypeVar("T")


_GENERATOR_DONE_SENTINEL = object()

LOGGER = logging.getLogger(__name__)


async def limited_parallel[T](
    awaitables: Iterable[Coroutine[Any, Any, T]],
    limit: int,
    semaphore: asyncio.Semaphore | None = None,
) -> AsyncGenerator[T, None]:
    if semaphore is None:
        semaphore = asyncio.Semaphore(limit)

    it = iter(awaitables)
    tasks: set[asyncio.Task[T]] = set()

    async def wrap_with_semaphore(coro: Coroutine[Any, Any, T]) -> T:
        async with semaphore:
            return await coro

    # Initialize tasks until the limit is reached
    for _ in range(limit):
        try:
            aw = next(it)
        except StopIteration:
            break
        tasks.add(asyncio.create_task(wrap_with_semaphore(aw)))

    while tasks:
        # Wait for at least one task to complete
        done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        # Yield completed tasks instead of their results
        for task in done:
            yield task.result()

        # Start new tasks to replace completed ones
        for _ in range(len(done)):
            try:
                next_aw = next(it)
                tasks.add(asyncio.create_task(wrap_with_semaphore(next_aw)))
            except StopIteration:
                continue


async def merge_async_generators[T](
    generators: Iterable[AsyncGenerator[T, None]],
    limit: int,
) -> AsyncGenerator[T, None]:
    queue: asyncio.Queue[T | object] = asyncio.Queue()  # Update queue type hint
    active_generators = 0

    async def consume_generator(gen: AsyncGenerator[T, None]) -> None:
        nonlocal active_generators
        active_generators += 1
        try:
            async for item in gen:
                await queue.put(item)
        except Exception:
            LOGGER.exception(
                "Error consuming generator %s, unhandled exception",
                gen,
            )
        finally:
            active_generators -= 1
            await queue.put(_GENERATOR_DONE_SENTINEL)  # Use sentinel

    tasks = []
    gen_iter = iter(generators)

    # Start initial tasks up to the limit
    for _ in range(limit):
        try:
            gen = next(gen_iter)
            tasks.append(asyncio.create_task(consume_generator(gen)))
        except StopIteration:
            break

    # Keep track of how many generators we expect to finish
    expected_done_signals = len(tasks)
    done_signals_received = 0

    while done_signals_received < expected_done_signals:
        item = await queue.get()
        if item is _GENERATOR_DONE_SENTINEL:  # Check for sentinel
            done_signals_received += 1
            # Try to start a new task if there are more generators
            with suppress(StopIteration):
                next_gen = next(gen_iter)
                tasks.append(asyncio.create_task(consume_generator(next_gen)))
                expected_done_signals += 1

        # No more generators to start
        else:
            yield cast("T", item)  # Explicitly cast item to T

    # Ensure all tasks are complete (though they should be by now)
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
