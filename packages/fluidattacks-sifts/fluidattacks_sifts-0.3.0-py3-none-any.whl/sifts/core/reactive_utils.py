import asyncio
from collections.abc import AsyncIterable, Awaitable, Callable

import reactivex as rx
from reactivex import operators as ops
from reactivex.abc import ObserverBase, SchedulerBase
from reactivex.disposable import Disposable


def filter_async[T1](
    async_predicate: Callable[[T1], Awaitable[bool]],
) -> Callable[[rx.Observable[T1]], rx.Observable[T1]]:
    """
    Filter elements from an Observable asynchronously using a predicate function.

    Example:
      async def is_valid(x: str) -> bool:
          result = await validate(x)
          return result

      # Usage:
      filtered = filter_async(is_valid)(sourceObservable)

    """

    def operator(x: T1) -> rx.Observable[T1]:
        # Create a future from the async predicate
        future = asyncio.ensure_future(async_predicate(x))
        bool_obs: rx.Observable[bool] = rx.from_future(future)

        # Define helper functions for the operators to improve type inference
        def filter_func(keep: bool) -> bool:  # noqa: FBT001
            return keep

        def map_func(_: bool) -> T1:  # noqa: FBT001
            return x

        result: rx.Observable[T1] = bool_obs.pipe(ops.filter(filter_func), ops.map(map_func))
        return result

    def _filter_async(source: rx.Observable[T1]) -> rx.Observable[T1]:
        return source.pipe(ops.flat_map(operator))

    return _filter_async


def from_async_generator[T1](async_gen: AsyncIterable[T1]) -> rx.Observable[T1]:
    """
    Create an Observable from an asynchronous generator.

    Converts an async generator into a reactive Observable where each generated
    item becomes an emission in the resulting Observable.

    Example:
      async def generate_data():
          for i in range(5):
              await asyncio.sleep(0.1)
              yield i

      # Usage:
      source = from_async_generator(generate_data())

    """

    def _subscribe(
        observer: ObserverBase[T1],
        scheduler: SchedulerBase | None = None,  # noqa: ARG001
    ) -> Disposable:
        async def _run() -> None:
            try:
                # iteramos sobre el async generator
                async for item in async_gen:
                    observer.on_next(item)
                observer.on_completed()
            except Exception as ex:  # noqa: BLE001
                observer.on_error(ex)

        # lanzamos la tarea en el loop actual
        task = asyncio.get_event_loop().create_task(_run())

        def dispose() -> None:
            task.cancel()

        return Disposable(dispose)

    return rx.create(_subscribe)


def map_async[T1, T2](
    mapper: Callable[[T1], Awaitable[T2]],
) -> Callable[[rx.Observable[T1]], rx.Observable[T2]]:
    """
    Transform each element of the source Observable by applying an asynchronous mapper function.

    Example:
      async def foo(x: str, y: str) -> int:
          result = await operation(x, y)
          return result

      # Usage:
      source = map_async(lambda i: foo(i, "some_value"))(sourceObservable)

    """

    def operator(x: T1) -> rx.Observable[T2]:
        future = asyncio.ensure_future(mapper(x))
        return rx.from_future(future)

    def _map_async(source: rx.Observable[T1]) -> rx.Observable[T2]:
        return source.pipe(ops.flat_map(operator))

    return _map_async
