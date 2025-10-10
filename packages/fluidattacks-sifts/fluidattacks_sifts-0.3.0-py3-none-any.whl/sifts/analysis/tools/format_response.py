import json
import logging

import pydantic
from agents.run_context import RunContextWrapper

from sifts.analysis.types import FunctionTool, TreeExecutionContext, VulnerabilityAssessment

LOGGER = logging.getLogger(__name__)


async def format_response(
    _ctx: RunContextWrapper[TreeExecutionContext],
    args: str,
) -> VulnerabilityAssessment | None:
    try:
        parsed = VulnerabilityAssessment.model_validate(
            json.loads(args),
            strict=False,
        )
    except pydantic.ValidationError:
        LOGGER.exception("Invalid JSON input: %s", args)
        return None
    except (TypeError, KeyError, AttributeError):
        LOGGER.exception("Invalid JSON input: %s", args)
        return None
    except Exception:
        LOGGER.exception("Invalid JSON input: %s", args)
        return None
    return parsed


FORMAT_RESPONSE = FunctionTool(
    name="format_response",
    description=(
        "Retrieves code and details using its ID from the global search. "
        "Use this after finding a relevant function with list_symbols. "
        "This will add the function to the available methods for analysis."
    ),
    params_json_schema={
        **VulnerabilityAssessment.model_json_schema(),
        "additionalProperties": False,
    },
    on_invoke_tool=format_response,
)
