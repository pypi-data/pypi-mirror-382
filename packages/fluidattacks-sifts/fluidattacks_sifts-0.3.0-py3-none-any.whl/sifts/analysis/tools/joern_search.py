import json
import tempfile
from pathlib import Path
from typing import Any, cast

import aiofiles
from agents import RunContextWrapper
from fluidattacks_core.cpg.joern import run_joern_command
from pydantic import BaseModel, Field, ValidationError

from sifts.analysis.types import FunctionTool, TreeExecutionContext
from sifts.core.types import Language as SiftsLanguage
from sifts.cpg import load_cpg_graph_binary
from sifts.io.tree import get_node_by_line


async def run_joern_command_with_temp_output(
    command: str,
    args: list[str],
    cpg_path: Path,
) -> dict[str, Any]:
    """Run joern-parser command and return parsed JSON result."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
        temp_path = Path(temp_file.name)

        try:
            # Add output file to args
            full_args = [command, str(cpg_path), *args, str(temp_path)]

            await run_joern_command("joern-parser", full_args)
            # Read and parse the JSON result
            async with aiofiles.open(temp_path) as f:
                content = await f.read()
                loaded = json.loads(content)

            # Normalize to dict structure for downstream consumers
            if isinstance(loaded, list):
                result: dict[str, Any] = {
                    "summary": {"totalResults": len(loaded)},
                    "results": loaded,
                }
            elif isinstance(loaded, dict):
                result = loaded
            else:
                result = {"summary": {"totalResults": 0}, "results": []}

            return result

        finally:
            # Clean up temporary file
            if temp_path.exists():
                temp_path.unlink()


async def get_cpg_path(
    working_dir: Path,
    language: SiftsLanguage,
    exclude: list[Path] | None = None,
) -> Path | None:
    """Get CPG path, loading it if necessary."""
    return await load_cpg_graph_binary(working_dir, language, exclude)


def _extract_entry_coords(
    entry: dict[str, Any],
) -> tuple[str | None, str | None, int | None, int | None]:
    """Extract name, file and line range from a joern result entry."""
    name = entry.get("name") or entry.get("methodName") or None
    file_name = entry.get("fileName")
    line_start = (
        entry.get("lineNumberStart")
        if entry.get("lineNumberStart") is not None
        else entry.get("lineNumber")
    )
    line_end = (
        entry.get("lineNumberEnd")
        if entry.get("lineNumberEnd") is not None
        else entry.get("lineNumber")
    )
    return (
        name if isinstance(name, str) else None,
        file_name if isinstance(file_name, str) else None,
        line_start if isinstance(line_start, int) else None,
        line_end if isinstance(line_end, int) else None,
    )


async def _generate_node_id(
    file_name: str,
    line_start: int,
    line_end: int | None = None,
    working_dir: Path | None = None,
) -> int | None:
    """Generate a node_id for tree-sitter node lookup based on line coordinates."""
    if not working_dir or not file_name:
        return None
    if line_end == line_start:
        line_end = None
    file_path = Path(working_dir, file_name)
    if not file_path.exists():
        return None
    node = await get_node_by_line(file_path, line_start, line_end)
    if node is None:
        return None
    return int(f"{node.start_byte}777{node.end_byte}")


async def _compact_entry(
    entry: dict[str, Any],
    item_fields: list[str],
    working_dir: Path | None = None,
) -> dict[str, Any] | None:
    """Build a compact entry and enrich with node_id if possible."""
    compact = {k: entry.get(k) for k in item_fields if k in entry}
    if not compact:
        return None
    _, file_name, line_start, line_end = _extract_entry_coords(entry)
    if not file_name or not line_start:
        return None
    node_id = await _generate_node_id(file_name, line_start, line_end, working_dir=working_dir)
    if node_id:
        compact["node_id"] = node_id
    return compact


async def _compact_response(
    raw: dict[str, Any],
    *,
    item_fields: list[str],
    max_items: int = 25,
    working_dir: Path | None = None,
) -> dict[str, Any]:
    """
    Reduce joern-parser JSON to a compact summary for the LLM.

    - exists: whether results are present
    - count: totalResults from summary (fallback to len(results))
    - items: up to max_items with only selected fields present in results
    """
    summary_obj = cast(dict[str, Any], raw.get("summary") or {})
    results_obj = cast(list[dict[str, Any]], raw.get("results") or raw.get("callChains") or [])

    total = summary_obj.get("totalResults")
    count = total if isinstance(total, int) else len(results_obj)

    items: list[dict[str, Any]] = []
    for entry in results_obj[:max_items]:
        compact = await _compact_entry(entry, item_fields, working_dir=working_dir)
        if compact:
            items.append(compact)

    return {"exists": count > 0, "count": count, "items": items}


# Search Classes
class SearchClassesArgs(BaseModel):
    name: str | None = Field(default=None, description="Name pattern to search for")
    full_name: str | None = Field(default=None, description="Full name pattern to search for")
    inheritance: str | None = Field(default=None, description="Inheritance pattern to search for")
    limit: int = Field(default=100, description="Maximum number of results")


async def search_classes(ctx: RunContextWrapper[TreeExecutionContext], args: str) -> str:
    """Search for classes matching specific patterns."""
    try:
        parsed = SearchClassesArgs.model_validate(json.loads(args), strict=False)
    except ValidationError as e:
        return f"Invalid JSON input: {e}"

    cpg_path = await get_cpg_path(
        ctx.context.working_dir, ctx.context.language, ctx.context.exclude
    )
    if not cpg_path:
        return "Failed to load or generate CPG file"

    search_args = ["--limit", str(parsed.limit)]
    if parsed.name:
        search_args.extend(["--name", parsed.name])
    if parsed.full_name:
        search_args.extend(["--full-name", parsed.full_name])
    if parsed.inheritance:
        search_args.extend(["--inheritance", parsed.inheritance])

    result = await run_joern_command_with_temp_output(
        "search-classes",
        search_args,
        cpg_path,
    )
    compact = await _compact_response(
        result,
        item_fields=[
            "name",
            "fullName",
            "fileName",
            "lineNumber",
            "lineNumberEnd",
            "packageName",
        ],
        working_dir=ctx.context.working_dir,
    )
    return json.dumps(compact, separators=(",", ":"))


SEARCH_CLASSES_TOOL = FunctionTool(
    name="search_classes",
    description="Search for classes matching specific patterns using Joern CPG analysis",
    params_json_schema={
        **SearchClassesArgs.model_json_schema(by_alias=False),
        "additionalProperties": False,
    },
    on_invoke_tool=search_classes,
)


# Search Methods
class SearchMethodsArgs(BaseModel):
    name: str | None = Field(default=None, description="Name pattern to search for")
    full_name: str | None = Field(default=None, description="Full name pattern to search for")
    class_name: str | None = Field(default=None, description="Class name to filter by")
    return_type: str | None = Field(default=None, description="Return type pattern")
    parameter_type: str | None = Field(default=None, description="Parameter type pattern")
    public: bool = Field(default=False, description="Filter by public methods")
    static: bool = Field(default=False, description="Filter by static methods")
    limit: int = Field(default=100, description="Maximum number of results")


async def search_methods(ctx: RunContextWrapper[TreeExecutionContext], args: str) -> str:
    """Search for methods matching specific patterns."""
    try:
        parsed = SearchMethodsArgs.model_validate(json.loads(args), strict=False)
    except ValidationError as e:
        return f"Invalid JSON input: {e}"

    cpg_path = await get_cpg_path(
        ctx.context.working_dir, ctx.context.language, ctx.context.exclude
    )
    if not cpg_path:
        return "Failed to load or generate CPG file"

    search_args = ["--limit", str(parsed.limit)]
    if parsed.name:
        search_args.extend(["--name", parsed.name])
    if parsed.full_name:
        search_args.extend(["--full-name", parsed.full_name])
    if parsed.class_name:
        search_args.extend(["--class", parsed.class_name])
    if parsed.return_type:
        search_args.extend(["--return-type", parsed.return_type])
    if parsed.parameter_type:
        search_args.extend(["--parameter-type", parsed.parameter_type])
    if parsed.public:
        search_args.append("--public")
    if parsed.static:
        search_args.append("--static")

    result = await run_joern_command_with_temp_output(
        "search-methods",
        search_args,
        cpg_path,
    )
    compact = await _compact_response(
        result,
        item_fields=[
            "name",
            "fullName",
            "fileName",
            "lineNumber",
            "lineNumberEnd",
            "className",
        ],
        working_dir=ctx.context.working_dir,
    )
    return json.dumps(compact, separators=(",", ":"))


SEARCH_METHODS_TOOL = FunctionTool(
    name="search_methods",
    description="Search for methods matching specific patterns using Joern CPG analysis",
    params_json_schema={
        **SearchMethodsArgs.model_json_schema(by_alias=False),
        "additionalProperties": False,
    },
    on_invoke_tool=search_methods,
)


# Search Calls
class SearchCallsArgs(BaseModel):
    name: str | None = Field(default=None, description="Name pattern to search for (method name)")
    caller: str | None = Field(default=None, description="Caller pattern to search for")
    callee: str | None = Field(default=None, description="Callee pattern to search for")
    file: str | None = Field(default=None, description="File name to filter by")
    limit: int = Field(default=100, description="Maximum number of results")


async def search_calls(ctx: RunContextWrapper[TreeExecutionContext], args: str) -> str:
    """Search for method calls matching specific patterns."""
    try:
        parsed = SearchCallsArgs.model_validate(json.loads(args), strict=False)
    except ValidationError as e:
        return f"Invalid JSON input: {e}"

    cpg_path = await get_cpg_path(
        ctx.context.working_dir, ctx.context.language, ctx.context.exclude
    )
    if not cpg_path:
        return "Failed to load or generate CPG file"

    search_args = ["--limit", str(parsed.limit)]
    if parsed.name:
        search_args.extend(["--name", parsed.name])
    if parsed.caller:
        search_args.extend(["--caller", parsed.caller])
    if parsed.callee:
        search_args.extend(["--callee", parsed.callee])
    if parsed.file:
        search_args.extend(["--file", parsed.file])

    result = await run_joern_command_with_temp_output(
        "search-calls",
        search_args,
        cpg_path,
    )
    compact = await _compact_response(
        result,
        item_fields=[
            "methodName",
            "caller",
            "callee",
            "fileName",
            "code",
            # "lineNumber",
            # "columnNumber",
        ],
        working_dir=ctx.context.working_dir,
    )
    return json.dumps(compact, separators=(",", ":"))


SEARCH_CALLS_TOOL = FunctionTool(
    name="search_calls",
    description="Search for method calls matching specific patterns using Joern CPG analysis",
    params_json_schema={
        **SearchCallsArgs.model_json_schema(by_alias=False),
        "additionalProperties": False,
    },
    on_invoke_tool=search_calls,
)


# Search Literals
class SearchLiteralsArgs(BaseModel):
    value: str | None = Field(default=None, description="Value pattern to search for")
    type: str | None = Field(default=None, description="Literal type to filter by")
    file: str | None = Field(default=None, description="File name to filter by")
    limit: int = Field(default=100, description="Maximum number of results")


async def search_literals(ctx: RunContextWrapper[TreeExecutionContext], args: str) -> str:
    """Search for literals/constants matching specific patterns."""
    try:
        parsed = SearchLiteralsArgs.model_validate(json.loads(args), strict=False)
    except ValidationError as e:
        return f"Invalid JSON input: {e}"

    cpg_path = await get_cpg_path(
        ctx.context.working_dir, ctx.context.language, ctx.context.exclude
    )
    if not cpg_path:
        return "Failed to load or generate CPG file"

    search_args = ["--limit", str(parsed.limit)]
    if parsed.value:
        search_args.extend(["--value", parsed.value])
    if parsed.type:
        search_args.extend(["--type", parsed.type])
    if parsed.file:
        search_args.extend(["--file", parsed.file])

    result = await run_joern_command_with_temp_output(
        "search-literals",
        search_args,
        cpg_path,
    )
    compact = await _compact_response(
        result,
        item_fields=["value", "type", "fileName", "lineNumber", "columnNumber"],
        working_dir=ctx.context.working_dir,
    )
    return json.dumps(compact, separators=(",", ":"))


SEARCH_LITERALS_TOOL = FunctionTool(
    name="search_literals",
    description="Search for literals/constants matching specific patterns using Joern CPG analysis",
    params_json_schema={
        **SearchLiteralsArgs.model_json_schema(by_alias=False),
        "additionalProperties": False,
    },
    on_invoke_tool=search_literals,
)


# Search Identifiers
class SearchIdentifiersArgs(BaseModel):
    name: str | None = Field(default=None, description="Name pattern to search for")
    type_pattern: str | None = Field(default=None, description="Type pattern to search for")
    file: str | None = Field(default=None, description="File name to filter by")
    limit: int = Field(default=100, description="Maximum number of results")


async def search_identifiers(ctx: RunContextWrapper[TreeExecutionContext], args: str) -> str:
    """Search for identifiers/variables matching specific patterns."""
    try:
        parsed = SearchIdentifiersArgs.model_validate(json.loads(args), strict=False)
    except ValidationError as e:
        return f"Invalid JSON input: {e}"

    cpg_path = await get_cpg_path(
        ctx.context.working_dir, ctx.context.language, ctx.context.exclude
    )
    if not cpg_path:
        return "Failed to load or generate CPG file"

    search_args = ["--limit", str(parsed.limit)]
    if parsed.name:
        search_args.extend(["--name", parsed.name])
    if parsed.type_pattern:
        search_args.extend(["--type-pattern", parsed.type_pattern])
    if parsed.file:
        search_args.extend(["--file", parsed.file])
    result = await run_joern_command_with_temp_output(
        "search-identifiers",
        search_args,
        cpg_path,
    )
    compact = await _compact_response(
        result,
        item_fields=[
            "name",
            "type",
            "fileName",
            "lineNumber",
            "columnNumber",
            "isLocal",
        ],
        working_dir=ctx.context.working_dir,
    )
    return json.dumps(compact, separators=(",", ":"))


SEARCH_IDENTIFIERS_TOOL = FunctionTool(
    name="search_identifiers",
    description=(
        "Search for identifiers/variables matching specific patterns using Joern CPG analysis"
    ),
    params_json_schema={
        **SearchIdentifiersArgs.model_json_schema(by_alias=False),
        "additionalProperties": False,
    },
    on_invoke_tool=search_identifiers,
)


# Search Imports
class SearchImportsArgs(BaseModel):
    import_pattern: str | None = Field(default=None, description="Import pattern to search for")
    file: str | None = Field(default=None, description="File name to filter by")
    limit: int = Field(default=100, description="Maximum number of results")


async def search_imports(ctx: RunContextWrapper[TreeExecutionContext], args: str) -> str:
    """Search for imports matching specific patterns."""
    try:
        parsed = SearchImportsArgs.model_validate(json.loads(args), strict=False)
    except ValidationError as e:
        return f"Invalid JSON input: {e}"

    cpg_path = await get_cpg_path(
        ctx.context.working_dir, ctx.context.language, ctx.context.exclude
    )
    if not cpg_path:
        return "Failed to load or generate CPG file"

    search_args = ["--limit", str(parsed.limit)]
    if parsed.import_pattern:
        search_args.extend(["--import", parsed.import_pattern])
    if parsed.file:
        search_args.extend(["--file", parsed.file])
    result = await run_joern_command_with_temp_output(
        "search-imports",
        search_args,
        cpg_path,
    )
    compact = await _compact_response(
        result,
        item_fields=["importedEntity", "importedAs", "fileName", "lineNumber", "isWildcard"],
        working_dir=ctx.context.working_dir,
    )
    return json.dumps(compact, separators=(",", ":"))


SEARCH_IMPORTS_TOOL = FunctionTool(
    name="search_imports",
    description="Search for imports matching specific patterns using Joern CPG analysis",
    params_json_schema={
        **SearchImportsArgs.model_json_schema(by_alias=False),
        "additionalProperties": False,
    },
    on_invoke_tool=search_imports,
)


# Search Namespaces
class SearchNamespacesArgs(BaseModel):
    name: str | None = Field(default=None, description="Name pattern to search for")
    limit: int = Field(default=100, description="Maximum number of results")


async def search_namespaces(ctx: RunContextWrapper[TreeExecutionContext], args: str) -> str:
    """Search for namespaces/packages matching specific patterns."""
    try:
        parsed = SearchNamespacesArgs.model_validate(json.loads(args), strict=False)
    except ValidationError as e:
        return f"Invalid JSON input: {e}"

    cpg_path = await get_cpg_path(
        ctx.context.working_dir, ctx.context.language, ctx.context.exclude
    )
    if not cpg_path:
        return "Failed to load or generate CPG file"

    search_args = ["--limit", str(parsed.limit)]
    if parsed.name:
        search_args.extend(["--name", parsed.name])
    result = await run_joern_command_with_temp_output(
        "search-namespaces",
        search_args,
        cpg_path,
    )
    compact = await _compact_response(
        result,
        item_fields=["name", "fullName", "fileName", "lineNumber"],
        working_dir=ctx.context.working_dir,
    )
    return json.dumps(compact, separators=(",", ":"))


SEARCH_NAMESPACES_TOOL = FunctionTool(
    name="search_namespaces",
    description=(
        "Search for namespaces/packages matching specific patterns using Joern CPG analysis"
    ),
    params_json_schema={
        **SearchNamespacesArgs.model_json_schema(by_alias=False),
        "additionalProperties": False,
    },
    on_invoke_tool=search_namespaces,
)


# Search Annotations
class SearchAnnotationsArgs(BaseModel):
    name: str | None = Field(default=None, description="Name pattern to search for")
    file: str | None = Field(default=None, description="File name to filter by")
    limit: int = Field(default=100, description="Maximum number of results")


async def search_annotations(ctx: RunContextWrapper[TreeExecutionContext], args: str) -> str:
    """Search for annotations matching specific patterns."""
    try:
        parsed = SearchAnnotationsArgs.model_validate(json.loads(args), strict=False)
    except ValidationError as e:
        return f"Invalid JSON input: {e}"

    cpg_path = await get_cpg_path(
        ctx.context.working_dir, ctx.context.language, ctx.context.exclude
    )
    if not cpg_path:
        return "Failed to load or generate CPG file"

    search_args = ["--limit", str(parsed.limit)]
    if parsed.name:
        search_args.extend(["--name", parsed.name])
    if parsed.file:
        search_args.extend(["--file", parsed.file])
    result = await run_joern_command_with_temp_output(
        "search-annotations",
        search_args,
        cpg_path,
    )
    compact = await _compact_response(
        result,
        item_fields=["name", "fullName", "fileName", "lineNumber"],
        working_dir=ctx.context.working_dir,
    )
    return json.dumps(compact, separators=(",", ":"))


SEARCH_ANNOTATIONS_TOOL = FunctionTool(
    name="search_annotations",
    description="Search for annotations matching specific patterns using Joern CPG analysis",
    params_json_schema={
        **SearchAnnotationsArgs.model_json_schema(by_alias=False),
        "additionalProperties": False,
    },
    on_invoke_tool=search_annotations,
)


# Search Fields
class SearchFieldsArgs(BaseModel):
    name: str | None = Field(default=None, description="Name pattern to search for")
    type_pattern: str | None = Field(default=None, description="Type pattern to search for")
    class_name: str | None = Field(default=None, description="Class name to filter by")
    static: bool = Field(default=False, description="Filter by static fields")
    private: bool = Field(default=False, description="Filter by private fields")
    limit: int = Field(default=100, description="Maximum number of results")


async def search_fields(ctx: RunContextWrapper[TreeExecutionContext], args: str) -> str:
    """Search for fields/attributes matching specific patterns."""
    try:
        parsed = SearchFieldsArgs.model_validate(json.loads(args), strict=False)
    except ValidationError as e:
        return f"Invalid JSON input: {e}"

    cpg_path = await get_cpg_path(
        ctx.context.working_dir, ctx.context.language, ctx.context.exclude
    )
    if not cpg_path:
        return "Failed to load or generate CPG file"

    search_args = ["--limit", str(parsed.limit)]
    if parsed.name:
        search_args.extend(["--name", parsed.name])
    if parsed.type_pattern:
        search_args.extend(["--type-pattern", parsed.type_pattern])
    if parsed.class_name:
        search_args.extend(["--class", parsed.class_name])
    if parsed.static:
        search_args.append("--static")
    if parsed.private:
        search_args.append("--private")
    result = await run_joern_command_with_temp_output(
        "search-fields",
        search_args,
        cpg_path,
    )
    compact = await _compact_response(
        result,
        item_fields=[
            "name",
            "type",
            "fileName",
            "lineNumber",
            "className",
            "isStatic",
            "isPrivate",
        ],
        working_dir=ctx.context.working_dir,
    )
    return json.dumps(compact, separators=(",", ":"))


SEARCH_FIELDS_TOOL = FunctionTool(
    name="search_fields",
    description="Search for fields/attributes matching specific patterns using Joern CPG analysis",
    params_json_schema={
        **SearchFieldsArgs.model_json_schema(by_alias=False),
        "additionalProperties": False,
    },
    on_invoke_tool=search_fields,
)
