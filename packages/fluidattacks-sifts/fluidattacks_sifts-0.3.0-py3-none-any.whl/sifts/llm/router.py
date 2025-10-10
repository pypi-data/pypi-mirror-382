import asyncio
import logging
import time
from typing import Any, Literal, Protocol, TypeVar, cast, override

import litellm
from litellm import (
    AlertingConfig,
    AllMessageValues,
    AllowedFailsPolicy,
    AssistantsTypedDict,
    DeploymentTypedDict,
    OptionalPreCallChecks,
    RetryPolicy,
    RouterGeneralSettings,
    RouterModelGroupAliasItem,
)
from litellm.router import Router as OriginalRouter
from litellm.types.utils import Choices as OriginalChoice
from litellm.types.utils import (
    EmbeddingResponse,
    GenericBudgetConfigType,
)
from litellm.types.utils import (
    Message as OriginalMessage,
)
from litellm.types.utils import ModelResponse as OriginalModelResponse

R = TypeVar("R", bound=OriginalRouter)

LOGGER = logging.getLogger(__name__)


class StrictMessage(OriginalMessage):
    content: str


class StrictModelChoice(OriginalChoice):
    message: StrictMessage


class StrictModelResponse(OriginalModelResponse):
    choices: list[StrictModelChoice]  # type: ignore [assignment]


class RouterStrict(Protocol):
    async def acompletion(
        self,
        model: str,
        messages: list[AllMessageValues],
        stream: Literal[False] = False,  # noqa: FBT002
        **kwargs: Any,  # noqa: ANN401
    ) -> StrictModelResponse: ...

    async def aembedding(
        self,
        model: str,
        input: str | list[str],  # noqa: A002
        is_async: bool | None = True,  # noqa: FBT002, FBT001
        **kwargs: Any,  # noqa: ANN401
    ) -> EmbeddingResponse: ...


def as_strict_router[R: OriginalRouter](router: R) -> RouterStrict:
    return cast("RouterStrict", router)


class ResilientRouter(OriginalRouter):
    @override
    def __init__(
        self,
        model_list: list[DeploymentTypedDict] | list[dict[str, Any]] | None = None,
        assistants_config: AssistantsTypedDict | None = None,
        redis_url: str | None = None,
        redis_host: str | None = None,
        redis_port: int | None = None,
        redis_password: str | None = None,
        cache_responses: bool | None = False,
        cache_kwargs: dict[str, Any] | None = None,
        caching_groups: list[tuple[Any, ...]] | None = None,
        client_ttl: int = 3600,
        polling_interval: float | None = None,
        default_priority: int | None = None,
        num_retries: int | None = None,
        max_fallbacks: int | None = None,
        timeout: float | None = None,
        stream_timeout: float | None = None,
        default_litellm_params: dict[str, Any] | None = None,
        default_max_parallel_requests: int | None = None,
        set_verbose: bool = False,
        debug_level: Literal["DEBUG", "INFO"] = "INFO",
        default_fallbacks: list[Any] | None = None,
        fallbacks: list[Any] | None = None,
        context_window_fallbacks: list[Any] | None = None,
        content_policy_fallbacks: list[Any] | None = None,
        model_group_alias: dict[str, str | RouterModelGroupAliasItem] | None = None,
        enable_pre_call_checks: bool = False,
        enable_tag_filtering: bool = False,
        retry_after: int = 0,
        retry_policy: RetryPolicy | dict[str, Any] | None = None,
        model_group_retry_policy: dict[
            str,
            RetryPolicy,
        ]
        | None = None,
        allowed_fails: int | None = None,
        allowed_fails_policy: AllowedFailsPolicy | None = None,
        cooldown_time: float | None = None,
        disable_cooldowns: bool | None = None,
        routing_strategy: Literal[
            "simple-shuffle",
            "least-busy",
            "usage-based-routing",
            "latency-based-routing",
            "cost-based-routing",
            "usage-based-routing-v2",
        ] = "simple-shuffle",
        optional_pre_call_checks: OptionalPreCallChecks | None = None,
        routing_strategy_args: dict[str, Any] | None = None,
        provider_budget_config: GenericBudgetConfigType | None = None,
        alerting_config: AlertingConfig | None = None,
        router_general_settings: RouterGeneralSettings | None = None,
    ) -> None:
        router_general_settings = router_general_settings or RouterGeneralSettings()

        super().__init__(
            model_list=model_list,
            assistants_config=assistants_config,
            redis_url=redis_url,
            redis_host=redis_host,
            redis_port=redis_port,
            redis_password=redis_password,
            cache_responses=cache_responses,
            cache_kwargs=cache_kwargs,  # type: ignore [arg-type]
            caching_groups=caching_groups,
            client_ttl=client_ttl,
            polling_interval=polling_interval,
            default_priority=default_priority,
            num_retries=num_retries,
            max_fallbacks=max_fallbacks,
            timeout=timeout,
            stream_timeout=stream_timeout,
            default_litellm_params=default_litellm_params,
            default_max_parallel_requests=default_max_parallel_requests,
            set_verbose=set_verbose,
            debug_level=debug_level,
            default_fallbacks=default_fallbacks,
            fallbacks=fallbacks,  # type: ignore [arg-type]
            context_window_fallbacks=context_window_fallbacks,  # type: ignore [arg-type]
            content_policy_fallbacks=content_policy_fallbacks,  # type: ignore [arg-type]
            model_group_alias=model_group_alias,
            enable_pre_call_checks=enable_pre_call_checks,
            enable_tag_filtering=enable_tag_filtering,
            retry_after=retry_after,
            retry_policy=retry_policy,
            model_group_retry_policy=model_group_retry_policy,  # type: ignore [arg-type]
            allowed_fails=allowed_fails,
            allowed_fails_policy=allowed_fails_policy,
            cooldown_time=cooldown_time,
            disable_cooldowns=disable_cooldowns,
            routing_strategy=routing_strategy,
            optional_pre_call_checks=optional_pre_call_checks,
            routing_strategy_args=routing_strategy_args,  # type: ignore [arg-type]
            provider_budget_config=provider_budget_config,
            alerting_config=alerting_config,
            router_general_settings=router_general_settings,
        )
        self.model_expiration_times: dict[str, float] = {}
        self._model_locks: dict[str, asyncio.Lock] = {}

    def _get_model_lock(self, model: str) -> asyncio.Lock:
        # Crea el lock si no existe para el modelo
        if model not in self._model_locks:
            self._model_locks[model] = asyncio.Lock()
        return self._model_locks[model]

    async def acompletion(  # type: ignore [override]
        self,
        model: str,
        messages: list[AllMessageValues],
        stream: bool = False,  # noqa: FBT001, FBT002
        **kwargs: Any,  # noqa: ANN401
    ) -> StrictModelResponse:
        model_lock = self._get_model_lock(model)
        async with model_lock:
            now = time.time()
            if model in self.model_expiration_times and now < self.model_expiration_times[model]:
                delay = self.model_expiration_times[model] - now
                await asyncio.sleep(delay)

            while True:
                try:
                    response = await super().acompletion(
                        model=model,
                        messages=messages,
                        stream=stream,
                        **kwargs,
                    )
                    return cast("StrictModelResponse", response)
                except litellm.exceptions.RateLimitError:
                    LOGGER.exception("Rate limit error for model %s", model)
                    self.model_expiration_times[model] = time.time() + 60
                    await asyncio.sleep(60)

    async def aembedding(
        self,
        model: str,
        input: str | list[str],  # noqa: A002
        is_async: bool | None = True,  # noqa: FBT001, FBT002
        **kwargs: Any,  # noqa: ANN401
    ) -> EmbeddingResponse:
        return await super().aembedding(model=model, input=input, is_async=is_async, **kwargs)
