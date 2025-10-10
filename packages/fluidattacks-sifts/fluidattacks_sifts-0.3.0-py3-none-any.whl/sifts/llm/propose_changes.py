import logging
from typing import TYPE_CHECKING

from sifts.llm.bedrock import get_bedrock_client
from sifts.llm.router import RouterStrict

if TYPE_CHECKING:
    from types_aiobotocore_bedrock_runtime.type_defs import MessageUnionTypeDef

MODELS = {
    "nova-pro": "arn:aws:bedrock:us-east-1:205810638802:application-inference-profile/9ty4xtwhwgu7",
    "nova-lite": "arn:aws:bedrock:us-east-1:205810638802:application-inference-profile/sgej46bmwi3u",  # noqa: E501
    "claude-3-5-haiku": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
    "llama4-maverick-17b-instruct": "us.meta.llama4-maverick-17b-instruct-v1:0",
}

LOGGER = logging.getLogger(__name__)


async def get_functional_semantics(
    *,
    router: RouterStrict,  # noqa: ARG001
    code: str,
) -> tuple[str | None, str | None]:
    abstract_propose_prompt: list[MessageUnionTypeDef] = [
        {
            "role": "user",
            "content": [
                {
                    "text": f"""{code}
What is the purpose of the function in the above code snippet? Please summarize the answer in one sentence using the following format:

"Function purpose: <summary>"

Make sure to describe the primary role of the function while considering all operations it performs,
such as encryption/decryption, logging, external method calls, data processing, or returning values.
Focus only on functional aspects, not security vulnerabilities.""",  # noqa: E501
                },
            ],
        },
    ]
    detailed_behavior_prompt: MessageUnionTypeDef = {
        "role": "user",
        "content": [
            {
                "text": f"""{code}
Please summarize the functions of the above code snippet by listing all notable functionalities it performs. Include operations such as encryption/decryption, key or IV handling, I/O processing, method calls, logging, exception handling, or any other relevant behaviors. Use the following format:

"The functions of the code snippet are:
1. <functionality>
2. <functionality>
3. <functionality>
..."

Do not evaluate security aspects or potential vulnerabilities; only describe the functional behavior of the code.""",  # noqa: E501
            },
        ],
    }

    client = await get_bedrock_client()
    response = await client.converse(
        modelId=MODELS["nova-lite"],
        messages=abstract_propose_prompt,
    )

    try:
        abstract_propose = response["output"]["message"]["content"][0]["text"]
    except (KeyError, IndexError):
        LOGGER.exception("Error getting functional semantics")
        return None, None

    response = await client.converse(
        modelId=MODELS["nova-lite"],
        messages=[detailed_behavior_prompt],
    )
    try:
        detailed_behavior = response["output"]["message"]["content"][0]["text"]
    except (KeyError, IndexError):
        LOGGER.exception("Error getting detailed behavior")
        return None, None
    return abstract_propose, detailed_behavior
