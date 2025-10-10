import logging
from functools import lru_cache
from pathlib import Path

import aiofiles
from asyncache import cached
from cachetools import Cache
from fluidattacks_core.serializers.syntax import (
    InvalidFileType,
    get_language_from_path,
    parse_content_tree_sitter,
)
from tree_sitter import Node, Tree

CACHE: Cache[str, Tree] = Cache(maxsize=1000)

LOGGER = logging.getLogger(__name__)


@cached(CACHE)  # type: ignore [misc]
async def _get_tree(file_path: Path, language: str) -> Tree:
    async with aiofiles.open(file_path, "rb") as f:
        content = await f.read()
    try:
        tree = parse_content_tree_sitter(content, language)
    except (OSError, InvalidFileType) as exc:
        msg = f"Error parsing tree for file '{file_path}'."
        raise ValueError(msg) from exc
    return tree


async def get_node_by_line(
    file_path: Path,
    line: int,
    line_end: int | None = None,
) -> Node | None:
    if line_end == -1:
        line_end = None
    language = lru_cache()(get_language_from_path)(str(file_path))
    if not language:
        return None

    # Find the largest node at the specified line
    target_node: Node | None = None
    node_size = 0

    def traverse_tree(node: Node) -> None:
        nonlocal target_node, node_size

        # Check if node contains the target line
        start_line = node.start_point[0]
        end_line = node.end_point[0]

        # Node must start at exactly the target line (not before)
        # and can span to multiple lines below
        if start_line in (line, line + 1, line - 1) and (
            end_line in (line_end, line_end + 1, line_end - 1) if line_end is not None else True
        ):
            # Calculate node size (number of lines it spans)
            current_size = end_line - start_line

            # If this node is larger than the current best match, update it
            if current_size > node_size or (current_size == node_size and target_node is None):
                target_node = node
                node_size = current_size

        # Recursively process children
        for child in node.children:
            traverse_tree(child)

    tree = await _get_tree(
        file_path,
        language,
    )
    # Start traversal from the root node
    traverse_tree(tree.root_node)
    if target_node is None:
        LOGGER.warning("Target node is not found: %s", file_path)
        return None
    return target_node
