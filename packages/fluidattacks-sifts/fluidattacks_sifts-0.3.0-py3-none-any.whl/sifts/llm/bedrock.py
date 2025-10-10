from collections.abc import Awaitable, Callable
from contextlib import AsyncExitStack
from typing import cast

import aioboto3
from types_aiobotocore_bedrock_runtime import (
    BedrockRuntimeClient,
)

StartupCallable = Callable[[], Awaitable[None]]
ShutdownCallable = Callable[[], Awaitable[None]]
GetResourceCallable = Callable[[], Awaitable[BedrockRuntimeClient]]
BedrockContext = tuple[StartupCallable, ShutdownCallable, GetResourceCallable]

SESSION = aioboto3.Session()


def create_bedrock_context() -> BedrockContext:
    context_stack = None
    resource = None

    async def _startup() -> None:
        nonlocal context_stack, resource

        context_stack = AsyncExitStack()
        resource = await context_stack.enter_async_context(
            SESSION.client(
                service_name="bedrock-runtime",
                use_ssl=True,
                verify=True,
            ),
        )
        if context_stack:
            await context_stack.aclose()

    async def _shutdown() -> None:
        if context_stack:
            await context_stack.aclose()

    async def _get_resource() -> BedrockRuntimeClient:
        if resource is None:
            await bedrock_startup()

        return cast(BedrockRuntimeClient, resource)

    return _startup, _shutdown, _get_resource


bedrock_startup, bedrock_shutdown, get_bedrock_client = create_bedrock_context()
