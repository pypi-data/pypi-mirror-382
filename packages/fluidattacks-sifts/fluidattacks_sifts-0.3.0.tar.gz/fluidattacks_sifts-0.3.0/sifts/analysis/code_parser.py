import asyncio
import fnmatch
import hashlib
import logging
import os
from collections.abc import AsyncGenerator, Generator
from contextlib import suppress
from dataclasses import dataclass
from datetime import UTC, datetime
from os import walk
from pathlib import Path
from string import Template
from typing import TYPE_CHECKING, Any, cast

import aioboto3
import aiofiles
from fluidattacks_core.serializers.snippet import find_function_name
from fluidattacks_core.serializers.syntax import (
    TREE_SITTER_FUNCTION_DECLARATION_MAP,
    InvalidFileType,
    extract_imports,
    get_language_from_path,
    parse_content_tree_sitter,
    query_nodes_by_language,
)
from snowflake.snowpark.functions import col
from snowflake_utils import create_session_manager
from tree_sitter import Node

import sifts
from sifts.analysis.agent_analysis import invoke_agent_gpt
from sifts.analysis.criteria import (
    generate_candidate_text,
)
from sifts.analysis.criteria_data import DEFINES_VULNERABILITIES
from sifts.analysis.types import (
    TreeExecutionContext,
)
from sifts.common_types.snippets import (
    num_tokens_from_string,
)
from sifts.config import SiftsConfig
from sifts.core.parallel_utils import limited_parallel
from sifts.core.repository import get_repo_head_hash
from sifts.cpg import (
    CallChain,
    MethodWithCallees,
    extract_path_from_cpg_call,
    load_cpg_graph_binary,
)
from sifts.io.db.base import DatabaseBackend
from sifts.io.db.dynamodb import get_prediction_by_snippet_hash
from sifts.io.db.types import AnalysisFacet, SafeFacet, VulnerableFacet
from sifts.io.db.types import SnippetFacet as Snippet
from sifts.io.file_system_defaults import TEST_FILES
from sifts.io.tree import get_node_by_line
from sifts.llm.config_data import MODEL_PARAMETERS

if TYPE_CHECKING:
    from snowflake.snowpark import Row
    from types_aiobotocore_bedrock_runtime.type_defs import MessageTypeDef


# Configuration Classes and Constants
class TokenLimits:
    """Constants for token limits in analysis."""

    MIN_TOKENS = 50
    MAX_SNIPPET_TOKENS = 3000
    MAX_PROCESSING_TOKENS = 10000
    MAX_FILE_LINES = 2000


class AnalysisParameters:
    """Constants for analysis parameters."""

    PARALLEL_LIMIT = 10
    MIN_SCORE_THRESHOLD = 0.5


EXCLUDED_LABELS = (
    "066. Technical information leak - Console functions",
    "234. Technical information leak - Stacktrace",
    "140. Insecure exceptions - Empty or no catch",
    "200. Traceability loss",
    "237. Technical information leak - Print Functions",
    "091. Log injection",
)


@dataclass
class SnowflakeConfig:
    """Configuration for Snowflake connection."""

    account: str
    user: str = "SIFTS"
    database: str = "SIFTS"
    schema: str = "SIFTS_CANDIDATES"
    private_key_path: str = ""

    @classmethod
    def from_env(cls) -> "SnowflakeConfig":
        return cls(
            account=os.getenv("SNOWFLAKE_ACCOUNT") or "",
            private_key_path=os.getenv("SNOWFLAKE_USER_PRIVATE_KEY") or "",
        )


class AnalysisError(Exception):
    """Base exception for analysis errors."""


class TokenLimitExceededError(AnalysisError):
    """Exception for when token limits are exceeded."""


class FileProcessingError(AnalysisError):
    """Exception for file processing errors."""


class SnippetCreationError(AnalysisError):
    """Exception for snippet creation errors."""


# Initialize global configuration
SNOWFLAKE_CONFIG = SnowflakeConfig.from_env()
SNOWFLAKE_SESSION_MANAGER_CANDIDATES = create_session_manager(
    account=SNOWFLAKE_CONFIG.account,
    user=SNOWFLAKE_CONFIG.user,
    private_key=SNOWFLAKE_CONFIG.private_key_path,
    database=SNOWFLAKE_CONFIG.database,
    schema=SNOWFLAKE_CONFIG.schema,
)
LOGGER = logging.getLogger(__name__)
SESSION = aioboto3.Session()


# Helper Functions
def _extract_function_name(method_node: Node, language: str) -> str | None:
    """Extract function name from a method node."""
    identifier_ = find_function_name([method_node], language)
    if identifier_:
        identifier_node, _ = identifier_
        text = identifier_node.text
        return text.decode("utf-8") if (text is not None) else text
    return None


async def create_snippet(  # noqa: PLR0913
    *,
    root_nickname: str,
    group_name: str,
    commit: str,
    where: str,
    method_node: Node,
    language: str,
    code: str,
) -> Snippet:
    """Create a snippet from a method node using unified format."""
    try:
        function_name = _extract_function_name(method_node, language)
        code_sha256 = hashlib.sha3_256(code.encode()).hexdigest()

        # Generate hash_id similar to generate-predictions
        hash_parts = [
            group_name,
            root_nickname,
            commit,
            where,
            method_node.type,
            str(method_node.start_byte),
            str(method_node.end_byte),
            str(method_node.start_point[0]),
            str(method_node.start_point[1]),
            str(method_node.end_point[0]),
            str(method_node.end_point[1]),
        ]
        hasher = hashlib.sha3_256()
        for part in hash_parts:
            hasher.update(part.encode("utf-8"))
        snippt_hash_id = hasher.hexdigest()

        return Snippet(
            snippet_hash_id=snippt_hash_id,
            group_name=group_name,
            root_nickname=root_nickname,
            commit=commit,
            path=where,
            start_byte=method_node.start_byte,
            end_byte=method_node.end_byte,
            start_line=method_node.start_point[0],
            start_column=method_node.start_point[1],
            end_line=method_node.end_point[0],
            end_column=method_node.end_point[1],
            node_type=method_node.type,
            code_sha256=code_sha256,
            created_at=datetime.now(UTC),
            text=code,
            language=language,
            name=function_name,
        )
    except ValueError as e:
        msg = f"Failed to create snippet: {e}"
        raise SnippetCreationError(msg) from e


async def has_existing_vulnerabilities(snippet: Snippet, db_backend: DatabaseBackend) -> bool:
    """Check if snippet already has vulnerability analyses."""
    previous_analyses = await db_backend.get_analyses_for_snippet(
        group_name=snippet.group_name,
        root_nickname=snippet.root_nickname,
        path=snippet.path,
        code_sha256=snippet.code_sha256,
        version=sifts.__version__,
    )
    return bool(previous_analyses)


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """Count tokens in text using specified model."""
    return num_tokens_from_string(text, model)


def is_within_snippet_limits(snippet: Snippet) -> bool:
    """Check if snippet is within token limits."""
    count = count_tokens(snippet.text or "")
    if count > TokenLimits.MAX_SNIPPET_TOKENS:
        LOGGER.debug(
            "Code is too long to be processed: %s:%s, count: %s",
            snippet.path,
            snippet.start_line,
            count,
        )
        return False
    if count < TokenLimits.MIN_TOKENS:
        LOGGER.debug(
            "Code is too short to be processed: %s:%s, count: %s",
            snippet.path,
            snippet.start_line,
            count,
        )
        return False
    return True


def is_within_processing_limits(code_enumerated: str) -> bool:
    """Check if enumerated code is within processing token limits."""
    count = count_tokens(code_enumerated)
    if count > TokenLimits.MAX_PROCESSING_TOKENS:
        return False
    return not count < TokenLimits.MIN_TOKENS


def create_enumerated_code(snippet: Snippet, prompt_lines: list[str] | None = None) -> str:
    """Create enumerated code from snippet."""
    if prompt_lines:
        return "\n".join(prompt_lines)

    return "\n".join(
        f"{index}| {x}"
        for index, x in enumerate(
            (snippet.text or "").split("\n"),
            start=snippet.start_line or 0,
        )
    )


def create_first_message(
    *,
    code_enumerated: str,
    snippet: Snippet,
    candidate_text: str,
    imports: str,
    strict: bool = True,
) -> "MessageTypeDef":
    """Create the first message for LLM analysis."""
    return {
        "role": "user",
        "content": [
            {
                "text": Template(
                    MODEL_PARAMETERS["prompts"]["agents"]["vuln_strict"]["instructions"]
                    if strict
                    else MODEL_PARAMETERS["prompts"]["agents"]["vuln_loose"]["instructions"],
                ).safe_substitute(
                    code=code_enumerated,
                    function_name=snippet.name,
                    vulnerability_knowledge=candidate_text,
                    filePath=snippet.path,
                    imports=imports,
                ),
            },
        ],
    }


async def _process_single_candidate_group(  # noqa: PLR0911, PLR0913
    candidates_group: tuple[str, ...],
    context: TreeExecutionContext,
    snippet: Snippet,
    imports: str,
    db_backend: DatabaseBackend,
    *,
    strict: bool = True,
    candidate_index: int,
    prompt_lines: list[str],
) -> AnalysisFacet | None:
    candidate_id = "-".join(sorted(candidates_group))
    previous_analyses = await db_backend.get_analyses_for_snippet_vulnerability(
        group_name=snippet.group_name,
        root_nickname=snippet.root_nickname,
        version=sifts.__version__,
        path=snippet.path,
        code_sha256=snippet.code_sha256,
        vulnerability_id=candidate_id,
    )
    if previous_analyses:
        return None

    candidate_text = generate_candidate_text(candidates_group)
    if not candidate_text:
        return None
    code_enumerated = create_enumerated_code(snippet, prompt_lines)

    if not is_within_processing_limits(code_enumerated):
        return None

    first_message = create_first_message(
        code_enumerated=code_enumerated,
        snippet=snippet,
        candidate_text=candidate_text,
        imports=imports,
        strict=strict,
    )
    result, usage = await invoke_agent_gpt(
        context=context,
        user_question=first_message["content"][0]["text"],
    )
    if result is None:
        return None
    cost = 0
    if result.is_vulnerable and result.vulnerability_type:
        if snippet.name is not None and result.vulnerable_function != snippet.name:
            return None
        finding_code = candidates_group[0]
        return VulnerableFacet(
            group_name=snippet.group_name,
            root_nickname=snippet.root_nickname,
            version=sifts.__version__,
            commit=get_repo_head_hash(context.working_dir) or "",
            analyzed_at=datetime.now(UTC),
            path=snippet.path,
            cost=cost,
            vulnerability_id_candidates=list(candidates_group),
            vulnerable_lines=result.vulnerable_lines or [],
            ranking_score=0,
            reason=result.explanation,
            input_tokens=usage["prompt_tokens"],
            output_tokens=usage["completion_tokens"],
            total_tokens=usage["total_tokens"],
            suggested_criteria_code=finding_code,
            suggested_finding_title=DEFINES_VULNERABILITIES[finding_code]["en"]["title"],
            snippet_hash_id=snippet.snippet_hash_id,
            code_hash=snippet.code_sha256,
        )

    return SafeFacet(
        group_name=snippet.group_name,
        root_nickname=snippet.root_nickname,
        version=sifts.__version__,
        commit=get_repo_head_hash(context.working_dir) or "",
        snippet_hash_id=snippet.snippet_hash_id,
        code_hash=snippet.code_sha256,
        analyzed_at=datetime.now(UTC),
        path=snippet.path,
        cost=cost,
        candidate_index=candidate_index,
        trace_id=None,
        input_tokens=usage["prompt_tokens"],
        output_tokens=usage["completion_tokens"],
        total_tokens=usage["total_tokens"],
        reason=result.explanation,
        vulnerability_id_candidates=list(candidates_group),
    )


async def _extract_code_and_imports(
    *,
    working_dir: Path,
    where: Path,
    method_node: Node,
) -> tuple[str, str, str] | None:
    try:
        async with aiofiles.open(working_dir / where, "rb") as f:
            file_content = await f.read()

        code = (
            method_node.text.decode(encoding="utf-8", errors="ignore")
            if method_node.text is not None
            else file_content[method_node.start_byte : method_node.end_byte].decode(
                encoding="utf-8",
                errors="ignore",
            )
        )
        language = get_language_from_path(str(where))
    except FileNotFoundError:
        LOGGER.warning("File not found: %s", where)
        return None
    except UnicodeDecodeError:
        LOGGER.warning("File is not UTF-8 encoded: %s", where)
        return None
    else:
        if not language or not code:
            return None
        try:
            imports_nodes = extract_imports(
                file_content.decode(encoding="utf-8", errors="ignore"),
                language,
            )
        except UnicodeDecodeError:
            LOGGER.warning("File is not UTF-8 encoded: %s", where)
            return None
        imports = "\n".join([(x.text or b"").decode() for x in imports_nodes])
        return code, imports, language


async def _extract_dangerous_methods(
    *,
    context: TreeExecutionContext,
    where: Path,
    snippet: Snippet,
) -> list[CallChain] | None:
    cpg_graph_path = await load_cpg_graph_binary(
        context.working_dir,
        context.language,
        tuple(Path(x) for x in context.exclude or []),
    )
    if cpg_graph_path is None:
        return None

    result = await extract_path_from_cpg_call(
        cpg_graph_path,
        (context.analysis_dir / where).relative_to(context.working_dir),
        snippet.start_line,
        snippet.end_line,
    )
    path = result.get("callChains", [])
    if not path:
        LOGGER.warning("No flow path found for %s", where)

    return path


async def _prepare_snippet(
    *,
    context: TreeExecutionContext,
    where: Path,
    method_node: Node,
    config: SiftsConfig,
    db_backend: DatabaseBackend,
) -> tuple[Snippet, str] | None:
    """Extract code, create and persist a snippet, and check for existing vulnerabilities."""
    # the where is relative to the analysis root, not the working dir
    extraction = await _extract_code_and_imports(
        working_dir=context.analysis_dir,
        where=where,
        method_node=method_node,
    )
    if extraction is None:
        return None

    code, imports, language = extraction

    snippet = await create_snippet(
        root_nickname=config.context.root_nickname or "",
        group_name=config.context.group_name or "",
        commit=get_repo_head_hash(context.working_dir) or "",
        where=str(where),
        method_node=method_node,
        language=language,
        code=code,
    )

    await db_backend.insert_snippet(snippet)
    if await has_existing_vulnerabilities(snippet, db_backend):
        return None

    if not snippet.text:
        return None

    return snippet, imports


async def _process_method_call(
    context: TreeExecutionContext,
    method_with_callees: MethodWithCallees,
    seen_ids: set[int],
    prompt_lines_flow: list[str],
) -> None:
    """Process a single method call and add its prompt lines."""
    method_item = method_with_callees["method"]
    node = await get_node_by_line(
        context.working_dir / method_item["fileName"],
        method_item["lineNumberStart"],
        method_item["lineNumberEnd"],
    )
    if node is None or node.text is None or hash(node.text) in seen_ids:
        return

    seen_ids.add(hash(node.text))
    prompt_lines_flow.append(f"## {method_item['fileName']} ({method_item['name']})")
    with suppress(UnicodeDecodeError, AttributeError):
        prompt_lines_flow.extend(
            f"{line_number}| {x}"
            for line_number, x in enumerate(
                node.text.decode(encoding="utf-8", errors="ignore").splitlines(),
                start=method_item["lineNumberStart"],
            )
        )


async def _get_method_flow_prompts(
    *,
    context: TreeExecutionContext,
    where: Path,
    snippet: Snippet,
) -> list[list[str]]:
    """Extract dangerous methods and format them into prompts."""
    method_flows = await _extract_dangerous_methods(
        context=context,
        where=where,
        snippet=snippet,
    )

    if not snippet.name:
        for flow_path in method_flows or []:
            # In the new schema, the target method is the last element in callPath
            if flow_path.get("callPath"):
                snippet.name = flow_path["callPath"][-1]["method"]["name"]
                break

    if not snippet.name:
        return []

    prompts_method_flows = []
    for flow_path in method_flows or []:
        prompt_lines_flow: list[str] = []
        seen_ids: set[int] = set()
        # In the new schema, iterate over callPath which contains MethodWithCallees objects
        for method_with_callees in flow_path.get("callPath", []):
            await _process_method_call(context, method_with_callees, seen_ids, prompt_lines_flow)
        prompts_method_flows.append(prompt_lines_flow)

    LOGGER.info("Number of method flows: %s", len(prompts_method_flows))
    return prompts_method_flows


async def _run_analysis_tasks(  # noqa: PLR0913
    *,
    context: TreeExecutionContext,
    snippet: Snippet,
    imports: str,
    candidate_codes: list[tuple[str, ...]],
    prompts_method_flows: list[list[str]],
    db_backend: DatabaseBackend,
) -> AsyncGenerator[AnalysisFacet | None, None]:
    """Create and run analysis tasks in parallel."""
    tasks = [
        _process_single_candidate_group(
            candidates_group=candidate_group,
            snippet=snippet,
            context=context,
            imports=imports,
            db_backend=db_backend,
            candidate_index=index,
            prompt_lines=prompt_lines_flow,
        )
        for index, candidate_group in enumerate(candidate_codes)
        for prompt_lines_flow in prompts_method_flows
    ]

    async for result in limited_parallel(tasks, limit=AnalysisParameters.PARALLEL_LIMIT):
        yield result


async def get_embedding_predictions_batch(
    *,
    context: TreeExecutionContext,
    snippet_hashes: list[str],
) -> dict[str, dict[str, Any]]:
    """Get embedding predictions for multiple snippets in a single query."""
    if not snippet_hashes:
        return {}

    labels_to_exclude = list(EXCLUDED_LABELS)
    df = context.snowflake_session.table("SIFTS_CANDIDATES.EMBEDDING_PREDICTIONS").filter(
        (col("CODE_HASH").isin(snippet_hashes))
        & (~col("PREDICTION_LABEL").isin(labels_to_exclude))
        & (col("PREDICTION_SCORE") > AnalysisParameters.MIN_SCORE_THRESHOLD)
    )
    async_job = df.collect_nowait()
    result = await asyncio.to_thread(async_job.result)
    result_rows: list[Row] = []
    if result:
        try:
            # Convert to list and filter out non-Row objects
            raw_rows = list(result)
            result_rows = [row for row in raw_rows if hasattr(row, "as_dict")]
        except (TypeError, ValueError):
            # Handle case where result is not iterable
            result_rows = []

    # Group results by CODE_HASH
    predictions_by_hash: dict[str, dict[str, Any]] = {}
    for row in result_rows:
        row_dict: dict[str, Any] = row.as_dict() if hasattr(row, "as_dict") else {}
        code_sha256 = cast(str, row_dict.get("CODE_HASH"))
        if code_sha256 not in predictions_by_hash:
            predictions_by_hash[code_sha256] = {
                "PREDICTION_LABEL": cast(str, row_dict.get("PREDICTION_LABEL")),
                "PREDICTION_SCORE": cast(float, row_dict.get("PREDICTION_SCORE")),
            }

    return predictions_by_hash


async def analyze_method_node(
    *,
    context: TreeExecutionContext,
    where: Path,
    method_node: Node,
    config: SiftsConfig,
    db_backend: DatabaseBackend,
) -> AsyncGenerator[AnalysisFacet | None, None]:
    """Analyzes a method node, processes it, and yields analysis results."""
    prepared_snippet = await _prepare_snippet(
        context=context,
        where=where,
        method_node=method_node,
        config=config,
        db_backend=db_backend,
    )
    if prepared_snippet is None:
        return

    snippet, imports = prepared_snippet
    snippet_content_hash = hashlib.sha3_256((snippet.text or "").encode()).hexdigest()

    prompts_method_flows = [
        [
            f"{line_number}| {x}"
            for line_number, x in enumerate(
                (method_node.text or b"").decode(encoding="utf-8", errors="ignore").splitlines(),
                start=snippet.start_line or 0,
            )
        ]
    ]

    # Get prediction data from DynamoDB
    prediction_data = await get_prediction_by_snippet_hash(
        code_hash=snippet_content_hash,
        version="V7",
    )

    candidate_codes: list[tuple[str, ...]] = []
    if (
        prediction_data
        and prediction_data["PREDICTION_LABEL"]
        and config.analysis.include_vulnerabilities
        and prediction_data["PREDICTION_LABEL"].split(".")[0]
        in config.analysis.include_vulnerabilities
        and prediction_data["PREDICTION_SCORE"] >= 0.2  # noqa: PLR2004
    ):
        candidate_codes = [(cast(str, prediction_data.get("PREDICTION_LABEL")).split(".")[0],)]

    async for result in _run_analysis_tasks(
        context=context,
        snippet=snippet,
        imports=imports,
        candidate_codes=candidate_codes,
        prompts_method_flows=prompts_method_flows,
        db_backend=db_backend,
    ):
        yield result


def _is_top_level_function(node: Node, function_node_names: set[str]) -> bool:
    parent = node.parent
    while parent:
        if parent.type in function_node_names:
            return False  # It's nested
        parent = parent.parent
    return True  # It's top-level


async def _process_files_with_walk(
    working_dir: Path,
    exclude_patterns: list[str],
    dir_wide_file_trigger_patterns: list[str],
) -> AsyncGenerator[tuple[str, Node], None]:
    for root, dirs, files in walk(working_dir, topdown=True):
        root_path = Path(root)
        root_str = str(root_path)

        if _should_skip_all_files_in_dir(files, root_path, dir_wide_file_trigger_patterns):
            dirs[:] = []
            continue

        dirs[:] = [
            d_name
            for d_name in dirs
            if not any(
                fnmatch.fnmatch(str(root_path / d_name), ex_pat) for ex_pat in exclude_patterns
            )
        ]

        if any(fnmatch.fnmatch(root_str, ex_pat) for ex_pat in exclude_patterns):
            continue

        for file_name in files:
            file_path = root_path / file_name
            file_path_str = str(file_path)

            if _should_skip_file(file_path_str, exclude_patterns):
                continue

            async for result in process_file_for_functions(
                file_path=file_path,
                working_dir=working_dir,
            ):
                yield result


async def _process_included_files_directly(
    working_dir: Path,
    include_patterns: list[str],
    exclude_patterns: list[str],
    start_working_dir: Path,  # Assumed to be validated as not None by caller
) -> AsyncGenerator[tuple[str, Node], None]:
    for included_file_rel_path_str in include_patterns:
        file_to_check = (start_working_dir / included_file_rel_path_str).resolve()

        if not (
            file_to_check.exists() and file_to_check.is_file()
        ) or not file_to_check.is_relative_to(working_dir.resolve()):
            continue

        file_path_str = str(file_to_check)

        if _should_skip_file(file_path_str, exclude_patterns):
            continue

        parent_dir = file_to_check.parent
        try:
            [f.name for f in parent_dir.iterdir() if f.is_file()]

        except OSError:
            continue

        async for result in process_file_for_functions(
            file_path=file_to_check,
            working_dir=working_dir,
        ):
            yield result


def _should_skip_all_files_in_dir(
    files: list[str],
    root_path: Path,
    dir_wide_file_trigger_patterns: list[str],
) -> bool:
    if not dir_wide_file_trigger_patterns:
        return False
    for file_name in files:
        file_path_str_for_trigger_check = str(root_path / file_name)
        if any(
            fnmatch.fnmatch(file_path_str_for_trigger_check, trigger_pat)
            for trigger_pat in dir_wide_file_trigger_patterns
        ):
            return True
    return False


def _should_skip_file(file_path_str: str, exclude_patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(file_path_str, ex_pat) for ex_pat in exclude_patterns)


async def iter_project_functions(
    working_dir: Path,
    exclude_patterns_param: list[str] | None,
    include_patterns_param: list[str] | None,
    start_working_dir: Path | None = None,
) -> AsyncGenerator[tuple[str, Node], None]:
    exclude_patterns = exclude_patterns_param if exclude_patterns_param is not None else []
    include_patterns = include_patterns_param if include_patterns_param is not None else []

    # Assuming TEST_FILES is defined in the global scope or imported
    dir_wide_file_trigger_patterns = [
        pat for pat in exclude_patterns if "." in pat and "*" in pat and pat not in TEST_FILES
    ]

    if include_patterns:
        if not start_working_dir:
            msg = "include_patterns were provided, but start_working_dir was not."
            raise ValueError(msg)
        # start_working_dir is confirmed to be Path here
        async for result in _process_included_files_directly(
            working_dir=working_dir,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            start_working_dir=start_working_dir,
        ):
            yield result
    else:
        async for result in _process_files_with_walk(
            working_dir=working_dir,
            exclude_patterns=exclude_patterns,
            dir_wide_file_trigger_patterns=dir_wide_file_trigger_patterns,
        ):
            yield result


async def process_file_for_functions(
    file_path: Path,
    working_dir: Path | None = None,
) -> AsyncGenerator[tuple[str, Node], None]:
    language = get_language_from_path(str(file_path))
    if not language:
        return
    try:
        async with aiofiles.open(file=file_path, mode="rb") as f:
            content = await f.read()
            try:
                tree = parse_content_tree_sitter(content, language)
            except (OSError, InvalidFileType):
                return
    except FileNotFoundError:
        return

    function_node_names = TREE_SITTER_FUNCTION_DECLARATION_MAP[language]
    function_nodes = query_nodes_by_language(
        language,
        tree,
        TREE_SITTER_FUNCTION_DECLARATION_MAP,
    )
    if len(content.splitlines()) > 2000:  # noqa: PLR2004
        LOGGER.warning(
            "File is too long to be processed: %s, count: %s",
            file_path,
            len(content.splitlines()),
        )
        return
    # Prevent minified files
    if (
        len(function_nodes) > 1
        and len({node.start_point[0] for node in (y for x in function_nodes.values() for y in x)})
        == 1
    ):
        return
    for node in (y for x in function_nodes.values() for y in x):
        if _is_top_level_function(node, set(function_node_names)):
            # Yield relative path from working_dir
            if working_dir:
                yield (str(file_path.relative_to(working_dir)), node)
            else:
                yield (str(file_path), node)


def search_nodes_in_tree(root_node: Node, line: int, node_types: tuple[str, ...]) -> Node | None:
    # First check if the current node is of the desired type and contains the line
    if root_node.type in node_types and root_node.start_point[0] <= line <= root_node.end_point[0]:
        return root_node

    # If this node doesn't contain the line we're looking for, no need to search its children
    if line < root_node.start_point[0] or line > root_node.end_point[0]:
        return None

    # Search in the children of the current node
    for child in root_node.children:
        result = search_nodes_in_tree(child, line, node_types)
        if result:
            return result

    return None


def traverse_tree(tree: Node) -> Generator[Node, None, None]:
    cursor = tree.walk()
    cursor.goto_first_child()
    cursor.goto_parent()

    reached_root = False
    while reached_root is False:
        if not cursor.node:
            break
        yield cursor.node

        if cursor.goto_first_child():
            continue

        if cursor.goto_next_sibling():
            continue

        retracing = True
        while retracing:
            if not cursor.goto_parent():
                retracing = False
                reached_root = True

            if cursor.goto_next_sibling():
                retracing = False


# Function aliases for backward compatibility and consistent naming
get_method_flow_prompts = _get_method_flow_prompts
extract_dangerous_methods = _extract_dangerous_methods
prepare_snippet = _prepare_snippet
extract_code_and_imports = _extract_code_and_imports
