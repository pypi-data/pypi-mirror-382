from string import Template
from typing import TYPE_CHECKING

from agents import Agent, Runner
from pydantic import BaseModel, Field

from sifts.llm.config_data import MODEL_PARAMETERS

if TYPE_CHECKING:
    from openai.types.responses import (
        ResponseInputItemParam,
    )


class Result(BaseModel):
    is_valid: bool = Field(
        description="When hypothesis is a good candidate for a more produce analysis",
    )
    reason: str = Field(description="The reason for the classification")


def get_agent() -> Agent:
    return Agent(
        name="Classifier",
        instructions=MODEL_PARAMETERS["prompts"]["agents"]["classify"]["system"],
        model="gpt-4.1",
        output_type=bool,
    )


async def classify_code(
    *,
    agent: Agent,
    code: str,
    vulnerability_knowledge: str,
    vulnerability_example: str,
) -> bool:
    first_message: ResponseInputItemParam = {
        "role": "user",
        "content": Template(
            MODEL_PARAMETERS["prompts"]["agents"]["classify"]["instructions"],
        ).safe_substitute(
            code=code,
            vulnerability_knowledge=vulnerability_knowledge,
            vulnerability_example=vulnerability_example,
        ),
    }
    response = await Runner.run(starting_agent=agent, input=[first_message])
    return bool(response.final_output)
