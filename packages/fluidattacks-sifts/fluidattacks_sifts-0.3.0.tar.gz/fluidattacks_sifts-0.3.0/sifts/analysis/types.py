from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Literal, NamedTuple, TypedDict, TypeVar

from agents.run_context import RunContextWrapper
from opensearchpy import AsyncOpenSearch
from pydantic import BaseModel, Field
from snowflake.snowpark import Session
from tinydb import TinyDB

from sifts.core.types import Language as SiftsLanguage

T = TypeVar("T")


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class VulnerabilityStatus(str, Enum):
    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"


class VulnerabilityAssessment(BaseModel):
    is_vulnerable: bool = Field(
        description="Final determination of vulnerability status ",
    )
    vulnerability_type: str | None = Field(
        description="Specific vulnerability category (e.g., 'SQL Injection', 'XSS', 'CSRF') or "
        "null if no vulnerability detected",
        default=None,
    )
    confidence: Literal["high", "medium", "low"] = Field(
        description="Confidence level based on code coverage completeness and clarity of "
        "vulnerability patterns",
    )
    explanation: str = Field(
        description="If the code is safe it generates a very short explanation."
        "But if the code is vulnerable, it generates a detailed explanation, including"
        "vulnerability mechanics, affected code paths,"
        "potential exploits, and supporting evidence from analyzed functions. ",
    )
    analyzed_functions: list[str] | None = Field(
        description="Comprehensive list of all function names examined during this assessment to "
        "document analysis coverage",
        default=None,
    )
    vulnerability_chain: list[str] | None = Field(
        description="Ordered sequence of functions that form the complete vulnerability path from"
        " entry point to exploitation point",
        default=None,
    )
    vulnerable_function: str | None = Field(
        description="Name of the specific function where the vulnerability was identified",
        default=None,
    )

    vulnerable_lines: list[int] | None = Field(
        description="Line numbers of the vulnerable function",
        default=None,
    )


class KindTypeScript(str, Enum):
    """Tags used by ctags to identify different code elements in TypeScript."""

    ALIAS = "alias"  # Alias in TypeScript (type aliases, import aliases)
    CLASS = "class"  # Classes in TypeScript
    CONSTANT = "constant"  # Constants/readonly variables
    ENUM = "enum"  # Enumerations
    ENUMERATOR = "enumerator"  # Individual values within an enumeration
    FUNCTION = "function"  # Functions (global or module-level)
    GENERATOR = "generator"  # Generator functions
    INTERFACE = "interface"  # Interfaces
    METHOD = "method"  # Methods (functions within classes)
    NAMESPACE = "namespace"  # Namespaces and modules
    PROPERTY = "property"  # Properties (class or interface members)
    VARIABLE = "variable"  # Variables (let, var, etc.)

    # The following types are disabled in the configuration but included for completeness
    LOCAL = "local"  # Local variables (disabled)
    PARAMETER = "parameter"  # Function/method parameters (disabled)

    @classmethod
    def from_string(cls, value: str) -> "KindTypeScript":
        """Convert a string to enum value, case-insensitive."""
        try:
            return cls(value.lower())
        except ValueError:
            # Default to FUNCTION if unknown
            return cls.FUNCTION

    @classmethod
    def enabled_kinds(cls) -> set[str]:
        """Return the set of enabled kinds from configuration."""
        return {
            cls.ALIAS.value,
            cls.CLASS.value,
            cls.CONSTANT.value,
            cls.ENUM.value,
            cls.ENUMERATOR.value,
            cls.FUNCTION.value,
            cls.GENERATOR.value,
            cls.INTERFACE.value,
            cls.METHOD.value,
            cls.NAMESPACE.value,
            cls.PROPERTY.value,
            cls.VARIABLE.value,
        }

    @classmethod
    def disabled_kinds(cls) -> set[str]:
        """Return the set of disabled kinds from configuration."""
        return {cls.LOCAL.value, cls.PARAMETER.value}


@dataclass
class TreeExecutionContext:
    working_dir: Path
    tiny_db: TinyDB
    snowflake_session: Session
    analysis_dir: Path
    open_client: AsyncOpenSearch
    language: SiftsLanguage
    exclude: list[Path] | None = None
    metadata: dict[str, Any] | None = None


class FunctionTool(NamedTuple):
    name: str
    description: str
    params_json_schema: dict[str, Any]
    on_invoke_tool: Callable[
        [RunContextWrapper[TreeExecutionContext], str], Coroutine[Any, Any, Any]
    ]


class Usage(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class JSONInputSchema(TypedDict):
    """Represents the JSON input schema for a Bedrock tool."""

    json: dict[str, Any]


class ToolSpecDict(TypedDict):
    """The specification (metadata + schema) that Bedrock expects for a single tool."""

    name: str
    description: str
    inputSchema: JSONInputSchema


class BedrockToolEntry(TypedDict):
    """
    Wrapper object that contains the tool specification. This matches the structure
    produced in `invoke_agent_bedrock` when building the tool configuration payload.
    """  # noqa: D205

    toolSpec: ToolSpecDict


class BedrockToolConfig(TypedDict):
    """Top-level container passed to Bedrock with all available tools."""

    tools: list[BedrockToolEntry]


class MessageTextContent(TypedDict):
    """A single text block inside the `content` array of a Bedrock message."""

    text: str


class BedrockUserMessage(TypedDict):
    """Representation of a user message in the Bedrock conversation format."""

    role: Literal["user"]
    content: list[MessageTextContent]
