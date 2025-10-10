import re
from typing import TYPE_CHECKING, Any

from litellm.utils import token_counter

from sifts.analysis.criteria import get_vuln_criteria
from sifts.llm.constants import MAX_TOKEN_COUNT_FUNCTION
from sifts.llm.router import RouterStrict

if TYPE_CHECKING:
    from litellm import AllMessageValues


def generate_vuln_context(vuln_criteria: dict[str, Any]) -> str:
    return (
        "# Vulnerability Context:\n"
        f"Title: {vuln_criteria['en']['title']}\n"
        f"Description: {vuln_criteria['en']['description']}\n"
        f"Recommendation: {vuln_criteria['en']['recommendation']}\n"
    )


def extract_function_code(llm_response: str) -> str | None:
    pattern = re.compile(r"<function>(?P<tag>.*?)</function>", re.DOTALL)
    match = pattern.search(llm_response)
    return match.group("tag") if match else None


async def fix_the_code(
    *,
    router: RouterStrict,
    finding_code: str,
    vulnerable_function: str,
    vulnerable_line_content: str,
    code_import: str | None = None,
) -> str | None:
    try:
        vuln_criteria = get_vuln_criteria(finding_code)
    except KeyError:
        return None

    vulnerability_context = generate_vuln_context(vuln_criteria)

    promt: tuple[AllMessageValues] = (
        {
            "content": (
                "You are an assistant who helps resolve vulnerabilities "
                "by rewriting vulnerable code and returning drop-in-place "
                "fixed code. The code should implement all needed "
                "adjustments to remediate the vulnerability.\n" + vulnerability_context
            ),
            "role": "user",
        },
        {
            "content": "Ok, show me the vulnerable code snippet",
            "role": "assistant",
        },
        {
            "content": (f"Vulnerable function: <code>\n{vulnerable_function}\n</code>"),
            "role": "user",
        },
        *(
            (
                {
                    "content": "Does this function use any imports?",
                    "role": "assistant",
                },
                {
                    "content": (
                        "Imports available in the module in which the function is"
                        " located\n<imports>\n" + "\n".join(code_import) + "\n</imports>"
                    ),
                    "role": "user",
                },
            )
            if code_import
            else ()
        ),
        {
            "content": "And where in the code is this vulnerability?",
            "role": "assistant",
        },
        {
            "content": (
                "The vulnerability is in the line that contains this"
                " fragment of code: <vulnerability>"
                f"\n{vulnerable_line_content}\n</vulnerability>"
            ),
            "role": "user",
        },
        {
            "content": "Got it. What do you want me to do in detail?",
            "role": "assistant",
        },
        {
            "content": (
                "# Requirements\n"
                "- Fix the code using the most secure alternative\n"
                "- Rewrite the new complete version of the function inside "
                "the <function></function> xml tags, do not use markdown "
                "Fenced Code Blocks. Your answer will be used to replace"
                " the function automatically, if you omit code the function "
                " will not work as expected\n"
                "- You must leave the function signature intact\n"
                "- Do not generate documentation for the function \n"
                "- You should not be brief \n"
                "- Do not leave comments within the code that I must complete"
                " manually \n"
                "- Implement all newly required methods in the steps\n"
                "- Write the new imports in the"
                " <imports></import> xml tag, outside of <function> tags\n"
                "- Avoid creating new classes\n"
            ),
            "role": "user",
        },
    )
    if token_counter(messages=list(promt)) > MAX_TOKEN_COUNT_FUNCTION + 1000:
        return None

    response = await router.acompletion(
        model="nova-pro",
        messages=list(promt),
        caching=True,
    )
    if not response.choices:
        return None
    return extract_function_code(response.choices[0].message.content)
