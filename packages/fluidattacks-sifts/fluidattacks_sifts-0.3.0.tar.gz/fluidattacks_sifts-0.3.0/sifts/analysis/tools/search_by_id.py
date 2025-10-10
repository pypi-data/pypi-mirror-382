import json
from pathlib import Path

import aiofiles
from agents import RunContextWrapper
from fluidattacks_core.serializers.syntax import (
    InvalidFileType,
    get_language_from_path,
    parse_content_tree_sitter,
)
from pydantic import BaseModel, Field
from pydantic_core import ValidationError
from tinydb.table import Document
from tree_sitter import Node

from sifts.analysis.types import FunctionTool, TreeExecutionContext


def _find_largest_node_at_line(root: Node, line: int) -> tuple[Node | None, int]:
    """
    Return the largest node that starts exactly at the given line.

    The size is computed as number of lines spanned by the node.
    """
    target_node: Node | None = None
    node_size = 0

    def traverse(node: Node) -> None:
        nonlocal target_node, node_size
        start_line = node.start_point[0]
        end_line = node.end_point[0]
        if start_line == line:
            current_size = end_line - start_line
            if current_size > node_size or (current_size == node_size and target_node is None):
                target_node = node
                node_size = current_size
        for child in node.children:
            if child.type in ("modifier",):
                continue
            traverse(child)

    traverse(root)
    return target_node, node_size


def _maybe_promote_to_parent(node: Node | None, line: int, node_size: int) -> Node | None:
    """If node is tiny, return a significantly larger parent that includes the line."""
    if node and (node.end_byte - node.start_byte) <= 10:  # noqa: PLR2004
        parent = node.parent
        if parent:
            parent_start = parent.start_point[0]
            parent_end = parent.end_point[0]
            parent_size = parent_end - parent_start
            if parent_start <= line <= parent_end and parent_size > node_size + 2:
                return parent
    return node


class GetFunctionByIdArgs(BaseModel):
    code_ids: list[int] = Field(
        description="IDs of the code you want to retrieve.",
    )
    path: str | None = Field(
        default=None,
        description=(
            "Optional path to the source file. Can be absolute or relative to working directory."
        ),
    )

    class Config:  # noqa: D106
        extra = "forbid"  # This is equivalent to additionalProperties: false


async def get_function_by_in_tree(
    working_dir: Path,
    document: Document,
) -> Node | None:
    language = get_language_from_path(str(Path(working_dir, document["path"])))
    try:
        line = document["line"] - 1
    except KeyError as exc:
        msg = f"Function with ID '{document.doc_id}' has no line number."
        raise ValueError(msg) from exc
    if not language:
        msg = f"Language not found for function with ID '{document.doc_id}'."
        raise ValueError(msg)
    async with aiofiles.open((Path(working_dir, document["path"])), "rb") as f:
        content = await f.read()
    try:
        tree = parse_content_tree_sitter(content, language)
    except (OSError, InvalidFileType) as exc:
        msg = f"Error parsing tree for function with ID '{document.doc_id}'."
        raise ValueError(msg) from exc

    # Find the largest node at the specified line and maybe promote to parent
    target_node, node_size = _find_largest_node_at_line(tree.root_node, line)
    return _maybe_promote_to_parent(target_node, line, node_size)


async def fetch_symbol_code(ctx: RunContextWrapper[TreeExecutionContext], args: str) -> str:
    try:
        parsed = GetFunctionByIdArgs.model_validate(json.loads(args))
    except ValidationError as e:
        return f"Invalid JSON input: {e}"
    result_methods = []
    for code_id in parsed.code_ids:
        code_id_str = str(code_id)

        if code_id_str in (ctx.context.metadata or {}).get("id_obtained", []):
            result_methods.append(
                f"Code with ID '{code_id}' already obtained. "
                "Please run search tools to obtain valid IDs."
            )

        # Check if it's a node_id (contains '777') or TinyDB document ID
        if "777" in code_id_str:
            # Handle node_id from search tools - path is required
            if not parsed.path:
                result_methods.append(
                    f"Path is required for code ID '{code_id_str}'. Please provide the file path."
                )
                continue
            result_methods.append(await _handle_node_id(ctx, code_id_str, parsed.path))

        # Handle TinyDB document ID - path not needed
        result_methods.append(await _handle_tinydb_id(ctx, code_id))
        if not ctx.context.metadata:
            ctx.context.metadata = {}
            ctx.context.metadata = {"id_obtained": [str(code_id)]}
        else:
            ctx.context.metadata["id_obtained"].append(str(code_id))

    return "\n".join(result_methods)


async def _handle_node_id(
    ctx: RunContextWrapper[TreeExecutionContext], node_id: str, file_path: str
) -> str:
    """Handle node_id from search tools (format: start_byte-end_byte)."""
    input_path = Path(file_path)
    full_path = (
        input_path if input_path.is_absolute() else Path(ctx.context.working_dir, input_path)
    )

    if not full_path.exists():
        return f"File not found: {full_path}"

    try:
        start_str, end_str = node_id.split("777")
        start_byte = int(start_str)
        end_byte = int(end_str)
    except (ValueError, IndexError) as exc:
        return f"Invalid ID format. Use the exact ID from search results. Error: {exc}"

    async with aiofiles.open(full_path, "rb") as f:
        file_content = await f.read()

    if start_byte >= len(file_content) or end_byte > len(file_content) or start_byte >= end_byte:
        return (
            "Invalid ID for the specified file. "
            "Verify the ID is correct and from recent search results."
        )

    segment = file_content[start_byte:end_byte]
    if not segment:
        return "Empty code segment for the specified ID."

    try:
        code_text = segment.decode("utf-8")
    except UnicodeDecodeError:
        code_text = segment.decode("utf-8", errors="replace")

    # Track the ID as obtained
    if not ctx.context.metadata:
        ctx.context.metadata = {}
        ctx.context.metadata = {"id_obtained": [node_id]}
    else:
        ctx.context.metadata["id_obtained"].append(node_id)

    return f"Node ID: {node_id}\n\nCode:\n{code_text}"


async def _handle_tinydb_id(ctx: RunContextWrapper[TreeExecutionContext], doc_id: int) -> str:
    """Handle TinyDB document ID."""
    tiny_db = ctx.context.tiny_db
    document = tiny_db.get(doc_id=doc_id)
    if isinstance(document, list):
        document = document[0] if document else None

    if document is None:
        return (
            f"Function with ID '{doc_id}' not found. Please run list_symbols to obtain valid IDs."
        )

    try:
        node = await get_function_by_in_tree(Path(ctx.context.working_dir), document)
    except ValueError as exc:
        return str(exc)
    if node is None or not node.text:
        return (
            f"Function with ID '{doc_id}' not found in the database. Please use"
            " list_symbols to find valid function IDs."
        )

    code = node.text.decode("utf-8")
    # Return the function code and metadata
    return f"Lines: {node.start_point.row}-{node.end_point.row}\n\nCode:\n{code}"


GET_FUNCTION_BY_ID_TOOL = FunctionTool(
    name="fetch_symbol_code",
    description=(
        "Retrieves code using an ID from search results. "
        "Use this after finding relevant code with search tools or list_symbols."
    ),
    params_json_schema={
        **GetFunctionByIdArgs.model_json_schema(),
        "additionalProperties": False,
        "required": ["code_ids"],
    },
    on_invoke_tool=fetch_symbol_code,
)
