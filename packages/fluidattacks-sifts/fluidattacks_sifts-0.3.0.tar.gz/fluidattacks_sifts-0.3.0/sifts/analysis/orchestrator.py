import fnmatch
import logging
import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from pathlib import Path

from aioboto3 import Session
from opensearchpy import AsyncOpenSearch
from tree_sitter import Node

import sifts
from sifts.analysis.code_parser import (
    SNOWFLAKE_SESSION_MANAGER_CANDIDATES,
    analyze_method_node,
    process_file_for_functions,
)
from sifts.analysis.types import TreeExecutionContext
from sifts.config import SiftsConfig
from sifts.core.parallel_utils import merge_async_generators
from sifts.core.repository import get_repo_head_hash
from sifts.core.types import Language as SiftsLanguage
from sifts.cpg import (
    TaintFlow,
    load_cpg_graph_binary,
)
from sifts.io.db.ctags_tinydb import create_tiny_db_from_ctags
from sifts.io.db.opensearch_client import setup_opensearch_client
from sifts.io.db.types import AnalysisFacet
from sifts.io.file_system import find_projects

SESSION = Session()
LOGGER = logging.getLogger(__name__)


async def analyze_project(
    *,
    config: SiftsConfig,
    context: TreeExecutionContext,
    exclude: list[str] | None = None,
) -> AsyncGenerator[AnalysisFacet | None, None]:
    function_iter = (
        iter_functions_from_line_config(context, config)
        if config.analysis.lines_to_check
        else iter_functions_from_project(
            context,
            config,
            exclude,
        )
    )
    if not await load_cpg_graph_binary(
        context.working_dir,
        context.language,
        tuple(Path(x) for x in exclude or []),
    ):
        LOGGER.info("No CPG graph found for project %s", config.analysis.working_dir)
        return

    function_pairs = []
    async for where, method_node in function_iter:
        function_pairs.append((where, method_node))

    LOGGER.info("Number of functions to analyze: %s", len(function_pairs))

    db_backend = config.get_database()
    function_coroutines = [
        analyze_method_node(
            method_node=method_node,
            where=where,
            context=context,
            config=config,
            db_backend=db_backend,
        )
        for where, method_node in function_pairs
    ]

    async for result in merge_async_generators(function_coroutines, limit=100):
        if result is not None:
            yield result


async def analyze_prompt(
    working_dir: Path,
    context: TreeExecutionContext,
    path: TaintFlow,
    config: SiftsConfig,
) -> AsyncGenerator[AnalysisFacet, None]:
    for node in await get_valid_functions(
        working_dir / path["targetMethod"]["fileName"],
        [path["targetMethod"]["lineNumberStart"]],
    ):
        db_backend = config.get_database()
        async for result in analyze_method_node(
            context=context,
            where=working_dir / Path(path["targetMethod"]["fileName"]),
            method_node=node,
            config=config,
            db_backend=db_backend,
        ):
            if result is not None:
                yield result


async def get_valid_functions(
    file_path: Path,
    lines: list[int],
) -> list[Node]:
    result: list[Node] = []
    async for _, node in process_file_for_functions(file_path):
        if any(x for x in lines if node.start_point[0] <= x <= node.end_point[0]):
            result.append(node)
    return result


async def iter_functions_from_line_config(
    context: TreeExecutionContext,
    config: SiftsConfig,
) -> AsyncGenerator[tuple[Path, Node], None]:
    """Async generator that yields functions to analyze based on line configs."""
    for line_config in config.analysis.lines_to_check:
        if not (config.analysis.working_dir / line_config.file).is_relative_to(
            context.working_dir,
        ):
            continue
        functions = await get_valid_functions(
            config.analysis.working_dir / line_config.file,
            line_config.lines,
        )
        for function in functions:
            where = (config.analysis.working_dir / line_config.file).relative_to(
                # config.analysis.working_dir,
                context.working_dir,
            )
            yield (
                where,
                function,
            )


async def iter_functions_from_project(
    context: TreeExecutionContext,
    config: SiftsConfig,
    exclude: list[str] | None = None,
) -> AsyncGenerator[tuple[Path, Node], None]:
    """
    Async generator that yields all functions for the files present in the TinyDB.

    This eliminates the redundant evaluation of exclusion patterns during the filesystem
    walk by relying exclusively on the list of files already collected in the TinyDB
    (which was generated with the desired exclusions).
    """
    # Collect unique relative file paths stored in the tiny DB
    tiny_db_paths: set[Path] = {
        Path(doc.get("path")) for doc in context.tiny_db.all() if doc.get("path") is not None
    }

    # Apply include/exclude patterns specified in the analysis config (these were NOT
    # necessarily applied when the TinyDB was generated).
    include_patterns = config.analysis.include_files or []
    exclude_patterns = set(config.analysis.exclude_files + (exclude or []))

    if include_patterns:
        tiny_db_paths = {
            p
            for p in tiny_db_paths
            if any(fnmatch.fnmatch(str(p), pat) for pat in include_patterns)
        }

    if exclude_patterns:
        tiny_db_paths = {
            p
            for p in tiny_db_paths
            if not any(fnmatch.fnmatch(str(p), pat) for pat in exclude_patterns)
        }

    # Iterate over each remaining path and yield its functions
    for rel_path in tiny_db_paths:
        full_path = (context.working_dir / rel_path).resolve()

        if not full_path.exists():
            LOGGER.debug("File %s does not exist", full_path)
            continue

        async for _, function_node in process_file_for_functions(
            file_path=full_path,
            working_dir=context.working_dir,
        ):
            try:
                where = full_path.relative_to(config.analysis.working_dir)
            except ValueError:
                where = rel_path
            yield (where, function_node)


@dataclass
class AnalysisContext:
    """Context object for project analysis."""

    config: SiftsConfig
    open_client: AsyncOpenSearch


async def setup_analysis_infrastructure(
    config: SiftsConfig,
) -> tuple[list[tuple[Path, SiftsLanguage, list[str]]], AsyncOpenSearch]:
    """Set up the analysis infrastructure including database, router, and opensearch client."""
    # Get database instance from configuration
    db_backend = config.get_database()
    await db_backend.startup()

    projects = find_projects(config.analysis.working_dir)
    open_client = await setup_opensearch_client()

    return projects, open_client


async def process_single_project(
    working_dir: Path,
    language: SiftsLanguage,
    exclude: list[str] | None,
    analysis_context: AnalysisContext,
) -> AsyncGenerator[AnalysisFacet, None]:
    """Process a single project and return its vulnerabilities."""
    config = analysis_context.config
    open_client = analysis_context.open_client

    if config.analysis.lines_to_check and not any(
        (config.analysis.working_dir / item.file).is_relative_to(working_dir)
        for item in config.analysis.lines_to_check
    ):
        return

    LOGGER.info(
        "Analyzing project %s",
        working_dir.relative_to(Path(config.analysis.working_dir)),
    )

    tiny_db, _ = await create_tiny_db_from_ctags(
        working_dir,
        exclude,
        language,
        metadata={
            "group_name": config.context.group_name,
            "root_nickname": config.context.root_nickname,
            "version": sifts.__version__,
            "commit": get_repo_head_hash(working_dir) or "",
            "uuid": str(uuid.uuid4()),
        },
    )

    context = TreeExecutionContext(
        working_dir=working_dir,
        tiny_db=tiny_db,
        analysis_dir=Path(config.analysis.working_dir),
        open_client=open_client,
        language=language,
        exclude=[Path(x) for x in exclude or []],
        snowflake_session=SNOWFLAKE_SESSION_MANAGER_CANDIDATES.get_session(),
    )

    try:
        # Get results from analyze_project_tree directly as AsyncGenerator
        async for response in analyze_project(
            context=context,
            config=config,
            exclude=exclude,
        ):
            if response is not None:
                # Process the result and add to our list
                db_backend = config.get_database()
                await db_backend.insert_analysis(response)
                yield response
    except Exception:
        LOGGER.exception(
            "Error in analysis for project %s",
            working_dir.relative_to(Path(config.analysis.working_dir)),
        )


async def collect_analysis_results(
    projects: list[tuple[Path, SiftsLanguage, list[str]]],
    analysis_context: AnalysisContext,
) -> list[AnalysisFacet]:
    """Collect analysis results from all projects with concurrency control."""
    all_results = []

    # Create coroutines for each project
    project_coroutines = [
        process_single_project(working_dir, language, exclude, analysis_context)
        for working_dir, language, exclude in projects
    ]

    # Use limited_as_completed to process projects with concurrency limit
    async for project_result in merge_async_generators(project_coroutines, limit=3):
        try:
            all_results.append(project_result)
        except Exception:
            LOGGER.exception("Error processing project")

    LOGGER.info("Total vulnerabilities found: %d", len(all_results))
    return all_results


async def scan_projects(config: SiftsConfig) -> list[AnalysisFacet]:
    """Scan projects and analyze vulnerabilities."""
    # Setup infrastructure
    projects, open_client = await setup_analysis_infrastructure(config)

    # Create analysis context
    analysis_context = AnalysisContext(
        config=config,
        open_client=open_client,
    )

    LOGGER.info("Number of projects: %s", len(projects))

    # Collect analysis results
    await collect_analysis_results(projects, analysis_context)

    return []
