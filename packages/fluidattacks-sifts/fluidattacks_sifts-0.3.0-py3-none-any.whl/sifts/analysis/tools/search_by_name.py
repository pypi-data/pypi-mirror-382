import json
import logging
from enum import Enum

from agents import RunContextWrapper

# OpenSearch
from pydantic import BaseModel, Field, ValidationError
from tinydb import Query, TinyDB
from tinydb.table import Document

from sifts.analysis.tools.fuzzy_matcher import fuzzy_match, get_search_terms
from sifts.analysis.types import FunctionTool, TreeExecutionContext

LOGGER = logging.getLogger(__name__)


class Kind(str, Enum):
    TYPEDEF = "typedef"
    NAMESPACE = "namespace"
    METHOD = "method"
    ENUMERATOR = "enumerator"
    STRUCT = "struct"
    CLASS = "class"
    INTERFACE = "interface"
    PROPERTY = "property"
    ENUM = "enum"
    FIELD = "field"
    FUNCTION = "function"
    CONSTANT = "constant"


class SearchFunctionByNameArgs(BaseModel):
    query: list[str] = Field(
        description=(
            "Names of the code element to search for. Avoid dot notation unless referring to"
            " scoped names like 'Class.method'."
        ),
    )
    kind: list[Kind] | None = Field(
        default=None,
        description="Type of the code element to search for.",
    )


def search_in_tinydb(
    db: TinyDB,
    parsed_args: SearchFunctionByNameArgs,
    exclude_scope_kinds: list[str] | None = None,
    name_threshold: int = 70,
) -> list[Document]:
    # Extract search terms
    search_names: list[str] = parsed_args.query
    search_terms = get_search_terms(*search_names)

    # Configure query object
    tag_accesor = Query()

    # Build query for the name using all search terms (OR logic)
    query_parts = [
        tag_accesor.name.test(
            lambda x, term=search_term: fuzzy_match(x, term, threshold=name_threshold),
        )
        for search_term in search_terms
    ]

    # Combine with OR logic
    query = query_parts[0]
    for part in query_parts[1:]:
        query = query | part

    # Add scope type filters
    if exclude_scope_kinds:
        for kind in exclude_scope_kinds:
            # Only exclude if the field exists and matches the excluded type
            query = query & ((~tag_accesor.scopeKind.exists()) | (tag_accesor.scopeKind != kind))
    if parsed_args.kind:
        query = query & (tag_accesor.kind.one_of(parsed_args.kind))
    # Execute the search
    results: list[Document] = db.search(query)

    # Filter for exact name matches first
    exact_matches = [doc for doc in results if doc.get("name") in parsed_args.query]

    # If exact matches found, return only those; otherwise return fuzzy matches
    if exact_matches:
        results = exact_matches

    # Sort results: first by path (descending) and then by line number (ascending) within the same
    # path
    results = sorted(results, key=lambda x: (x.get("path", ""), -x.get("line", 0)), reverse=True)

    # Apply results limitation if max_results is specified
    max_results = getattr(parsed_args, "max_results", 10)
    if max_results is not None:
        results = results[:max_results]

    return results


async def list_symbols(ctx: RunContextWrapper[TreeExecutionContext], args: str) -> str:
    try:
        parsed = SearchFunctionByNameArgs.model_validate(json.loads(args))
    except ValidationError as e:
        return f"Invalid JSON input: {e}"

    results = search_in_tinydb(ctx.context.tiny_db, parsed, name_threshold=70)

    if not results:
        filter_message = ""

        return (
            f"No functions found matching '{parsed.query}'{filter_message}. "
            f"Try a different search term or adjust the filters."
        )

    # Find corresponding graph nodes for methods and functions
    formatted_results = []
    for result in results:
        # Create a detailed string representation of the result
        function_type: str = result.get("kind", "unknown")
        scope_info: str = ""
        if "scope" in result and "scopeKind" in result:
            scope_info = f" - Defined in {result['scopeKind']} '{result['scope']}'"
        elif "scope" in result:
            scope_info = f" - Defined in '{result['scope']}'"

        # Clean up pattern by removing special characters at beginning and end, then trim
        pattern: str = result.get("pattern", "")
        if pattern:
            pattern = pattern.removeprefix("/^")
            pattern = pattern.removesuffix("$/")
            pattern = pattern.strip()

        formatted_results.append(
            f"ID: {result.doc_id} | {function_type.capitalize()}: {result['name']}{scope_info} | "
            f"File: {result['path']} | Snippet: {pattern}",
        )
    return "\n".join(formatted_results)


SEARCH_FUNCTION_TOOL = FunctionTool(
    name="list_symbols",
    description=(
        "Search for metadata about code elements (functions, classes, interfaces, constants) "
        "across the entire codebase by name. Use this tool to locate other definitions you may "
        "want to analyze further."
        "Returns matching element names, file paths, line numbers, and unique IDs — not full"
        " source code. "
        "To retrieve the full source, use the `fetch_symbol_code` tool with the returned ID."
    ),
    params_json_schema={
        **SearchFunctionByNameArgs.model_json_schema(),
        "additionalProperties": False,
    },
    on_invoke_tool=list_symbols,
)
