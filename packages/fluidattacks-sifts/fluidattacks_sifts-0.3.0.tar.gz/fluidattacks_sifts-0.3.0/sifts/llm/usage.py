import datetime
import logging
from collections.abc import Callable, Coroutine
from typing import Any

import aiosqlite
from agents import Usage

from sifts.llm.router import StrictModelResponse

LOGGER = logging.getLogger(__name__)


def generate_price_counter(
    group_name: str,
    root_id: str,
) -> Callable[
    [dict[str, Any], StrictModelResponse, datetime.datetime, datetime.datetime],
    Coroutine[Any, Any, None],
]:
    async def _async_test_logging_fn(
        kwargs: dict[str, Any],
        _completion_obj: StrictModelResponse,
        _start_time: datetime.datetime,
        _end_time: datetime.datetime,
    ) -> None:
        if _completion_obj.model_extra and "usage" in _completion_obj.model_extra:
            prompt_tokens = _completion_obj.model_extra["usage"].get("prompt_tokens", 0)
            completion_tokens = _completion_obj.model_extra["usage"].get("completion_tokens", 0)
        else:
            prompt_tokens = 0
            completion_tokens = 0
        completion_id = _completion_obj.id
        cost = kwargs["response_cost"]

        async with aiosqlite.connect("my_database.db") as db:
            await db.execute(
                """CREATE TABLE IF NOT EXISTS transactions (
                    completion_id TEXT PRIMARY KEY,
                    group_name TEXT NOT NULL,
                    root_id TEXT NOT NULL,
                    cost REAL NOT NULL,
                    prompt_tokens INTEGER NOT NULL,
                    completion_tokens INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )""",
            )
            await db.execute(
                """INSERT INTO transactions (completion_id, group_name, root_id, cost,
                prompt_tokens, completion_tokens)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (completion_id, group_name, root_id, cost, prompt_tokens, completion_tokens),
            )
            await db.commit()

    return _async_test_logging_fn


def calculate_cost(usage: Usage, model: str) -> float:
    input_tokens = usage.input_tokens
    output_tokens = usage.output_tokens
    # Assuming usage object might have cached_input_tokens, otherwise default to 0
    cached_input_tokens = getattr(usage, "cached_input_tokens", 0)
    cost = 0.0  # Initialize as float

    # Prices are per 1 million tokens, divide by 1,000,000 for per-token cost
    pricing_data: dict[str, dict[str, float | None]] = {
        "gpt-4.1": {"input": 2.00, "cached": 0.50, "output": 8.00},
        "gpt-4.1-mini": {"input": 0.40, "cached": 0.10, "output": 1.60},
        "gpt-4.1-nano": {"input": 0.10, "cached": 0.025, "output": 0.40},
        "gpt-4.5-preview": {"input": 75.00, "cached": 37.50, "output": 150.00},
        "gpt-4o": {"input": 2.50, "cached": 1.25, "output": 10.00},
        "gpt-4o-audio-preview": {"input": 2.50, "cached": None, "output": 10.00},
        "gpt-4o-realtime-preview": {"input": 5.00, "cached": 2.50, "output": 20.00},
        "gpt-4o-mini": {"input": 0.15, "cached": 0.075, "output": 0.60},
        "gpt-4o-mini-audio-preview": {"input": 0.15, "cached": None, "output": 0.60},
        "gpt-4o-mini-realtime-preview": {"input": 0.60, "cached": 0.30, "output": 2.40},
        "o1": {"input": 15.00, "cached": 7.50, "output": 60.00},
        "o1-pro": {"input": 150.00, "cached": None, "output": 600.00},
        "o3": {"input": 10.00, "cached": 2.50, "output": 40.00},
        "o4-mini": {"input": 1.10, "cached": 0.275, "output": 4.40},
        "o3-mini": {"input": 1.10, "cached": 0.55, "output": 4.40},
        "o1-mini": {"input": 1.10, "cached": 0.55, "output": 4.40},
        "gpt-4o-mini-search-preview": {"input": 0.15, "cached": None, "output": 0.60},
        "gpt-4o-search-preview": {"input": 2.50, "cached": None, "output": 10.00},
        "computer-use-preview": {"input": 3.00, "cached": None, "output": 12.00},
        "gpt-image-1": {"input": 5.00, "cached": None, "output": None},  # Output cost not specified
    }

    api_id_to_model_name = {
        "gpt-4.1-2025-04-14": "gpt-4.1",
        "gpt-4.1-mini-2025-04-14": "gpt-4.1-mini",
        "gpt-4.1-nano-2025-04-14": "gpt-4.1-nano",
        "gpt-4.5-preview-2025-02-27": "gpt-4.5-preview",
        "gpt-4o-2024-08-06": "gpt-4o",
        "gpt-4o-audio-preview-2024-12-17": "gpt-4o-audio-preview",
        "gpt-4o-realtime-preview-2024-12-17": "gpt-4o-realtime-preview",
        "gpt-4o-mini-2024-07-18": "gpt-4o-mini",
        "gpt-4o-mini-audio-preview-2024-12-17": "gpt-4o-mini-audio-preview",
        "gpt-4o-mini-realtime-preview-2024-12-17": "gpt-4o-mini-realtime-preview",
        "o1-2024-12-17": "o1",
        "o1-pro-2025-03-19": "o1-pro",
        "o3-2025-04-16": "o3",
        "o4-mini-2025-04-16": "o4-mini",
        "o3-mini-2025-01-31": "o3-mini",
        "o1-mini-2024-09-12": "o1-mini",
        "gpt-4o-mini-search-preview-2025-03-11": "gpt-4o-mini-search-preview",
        "gpt-4o-search-preview-2025-03-11": "gpt-4o-search-preview",
        "computer-use-preview-2025-03-11": "computer-use-preview",
        # "gpt-image-1" has no separate API ID in the image, assume model name is used directly
    }

    # Resolve API ID to model name if necessary
    model_name = api_id_to_model_name.get(model, model)

    # Get pricing for the resolved model name
    model_pricing = pricing_data.get(model_name)

    if model_pricing:
        # Safely get prices within the check
        input_cost_per_mil = model_pricing.get("input", 0) or 0
        output_cost_per_mil = model_pricing.get("output", 0) or 0
        cached_cost_per_mil = model_pricing.get("cached", 0) or 0

        input_cost = input_cost_per_mil / 1_000_000
        output_cost = output_cost_per_mil / 1_000_000
        cached_cost = cached_cost_per_mil / 1_000_000

        cost = (
            (input_tokens * input_cost)
            + (output_tokens * output_cost)
            + (cached_input_tokens * cached_cost)
        )
    else:
        # Handle unknown models or fallback if needed
        LOGGER.warning(
            "Pricing for model '%s' (resolved to '%s') not found. Cost calculated as 0.",
            model,
            model_name,
        )

    return cost
