import hashlib
import json
import logging
import re
import tempfile
from collections.abc import Iterable
from contextlib import suppress
from pathlib import Path
from typing import TypedDict, cast

import aiofiles
import aiofiles.os
from aioboto3 import Session
from fluidattacks_core.cpg import generate_cpg
from fluidattacks_core.cpg.joern import run_joern_command
from fluidattacks_core.filesystem.defaults import Language as SystemLanguage
from platformdirs import user_cache_dir

from sifts.core.types import Language as SiftsLanguage
from sifts.io.vcs.git import get_last_commit, get_repo_top_level


class CPGCall(TypedDict):
    methodName: str
    callCount: str


class CPGCallSummary(TypedDict):
    orderedExternalMethods: list[CPGCall]


class CPGCalls(TypedDict):
    summary: CPGCallSummary


class FlowNode(TypedDict):
    name: str
    fullName: str
    fileName: str
    lineNumberStart: int
    lineNumberEnd: int


class PathElement(TypedDict):
    nodeType: str
    tracked: str
    lineNumberStart: int
    lineNumberEnd: int
    method: str
    fileName: str


class MethodInfo(TypedDict):
    name: str
    fullName: str
    fileName: str
    lineNumberStart: int
    lineNumberEnd: int
    isExternal: bool


class CallSite(TypedDict):
    code: str
    lineNumber: int
    columnNumber: int
    fileName: list[str]


class CalleeWithDownChain(TypedDict):
    method: MethodInfo
    callSites: list[CallSite]
    downCallChain: list["CalleeWithDownChain"]
    downCallChainCount: int


class MethodWithCallees(TypedDict):
    method: MethodInfo
    callees: list[CalleeWithDownChain]


class CallChain(TypedDict):
    pathLength: int
    callPath: list[MethodWithCallees]


class AnalysisParameters(TypedDict):
    maxUpDepth: int
    maxDownDepth: int
    downSameFileOnly: bool
    maxDownFanout: int


class Summary(TypedDict):
    totalCallChains: int
    filePath: str
    lineNumberStart: int
    lineNumberEnd: int
    parameters: AnalysisParameters


class TaintFlow(TypedDict):
    # Keep old structure for backward compatibility, but add new fields
    targetMethod: FlowNode
    entryPoint: FlowNode
    methodsInFlow: list[FlowNode]
    callChain: list[FlowNode]
    # New schema fields
    pathLength: int
    callPath: list[MethodWithCallees]


class CPGPaths(TypedDict):
    summary: Summary
    callChains: list[CallChain]


LOGGER = logging.getLogger(__name__)


def transform_method_name(method_name: str) -> tuple[str | None, str | None]:
    if method_name.startswith(("<", "__")):
        return None, None
    if ":" in method_name:
        library, method = method_name.split(":", 1)
    elif "." in method_name:
        library, method = method_name.split(".", 1)
    else:
        return None, None
    method = re.sub(r"<[^>]+>", "", method)
    method_parts = [
        part
        for part in method.split(".")
        if part and not (part.startswith("__") and part.endswith("__"))
    ]
    method = ".".join(method_parts)
    if not method:
        return None, None
    return library, method


async def load_cpg_graph_binary(
    working_dir: Path,
    language: SiftsLanguage,
    exclude: Iterable[Path] | None = None,
) -> Path | None:
    exclude = exclude or []
    cache_dir = Path(user_cache_dir("sifts"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    try:
        relative_path = working_dir.relative_to(await get_repo_top_level(working_dir))
    except ValueError:
        relative_path = working_dir
    cache_file = (
        cache_dir
        / hashlib.sha3_256(
            (await get_last_commit(working_dir) + str(relative_path) + language.value).encode(),
        ).hexdigest()
    )
    if cache_file.exists():
        return cache_file
    async with Session().client("s3") as s3_client:
        with suppress(s3_client.exceptions.ClientError):
            await s3_client.head_object(
                Bucket="machine.data",
                Key=f"cpg/{cache_file.name}",
            )
            await s3_client.download_file(
                "machine.data",
                f"cpg/{cache_file.name}",
                str(cache_file.absolute()),
            )
            return cache_file
        cpg_file = await generate_cpg(working_dir, SystemLanguage(language.value), list(exclude))

        if not cpg_file:
            return None
        if not Path(cpg_file).exists():
            return None
        await s3_client.upload_file(
            str(cpg_file.absolute()),
            "machine.data",
            f"cpg/{cpg_file.name}",
        )

        return cpg_file


async def extract_path_from_cpg_call(
    graph_file: Path,
    file_path: Path,
    line_start: int,
    line_end: int,
) -> CPGPaths:
    # the file path must be relative to the working dir, because joern expects it that way
    with tempfile.NamedTemporaryFile(delete=False) as f:
        output_file = Path(f.name)
        args = [
            str(graph_file),  # inputPath
            str(output_file),  # outputJsonFile
            str(line_start - 1),  # lineNumberStart
            str(line_end),  # lineNumberEnd
            str(file_path),  # filePath
            "--max-up-depth",
            "16",
            "--max-down-depth",
            "3",
            "--down-same-file-only",
            "false",
            "--max-down-fanout",
            "25",
        ]
        await run_joern_command(
            "chain-of-call",
            args,
        )
        async with aiofiles.open(output_file) as file:
            try:
                return cast("CPGPaths", json.loads(await file.read()))
            except json.JSONDecodeError:
                empty_result: CPGPaths = {
                    "summary": {
                        "totalCallChains": 0,
                        "filePath": str(file_path),
                        "lineNumberStart": line_start,
                        "lineNumberEnd": line_end,
                        "parameters": {
                            "maxUpDepth": 16,
                            "maxDownDepth": 3,
                            "downSameFileOnly": False,
                            "maxDownFanout": 25,
                        },
                    },
                    "callChains": [],
                }
                return empty_result
