import asyncio
import logging
import os
import tempfile
from collections.abc import Generator
from concurrent.futures import ProcessPoolExecutor
from itertools import islice
from pathlib import Path
from typing import Any

import orjson
from opensearchpy import AsyncOpenSearch
from tinydb import TinyDB
from tinydb.storages import MemoryStorage

# Keep TinyDB insertion for in-memory use using the same IDs
from sifts.core.types import Language
from sifts.io.file_system import should_exclude

LOGGER = logging.getLogger(__name__)


def chunked_reader(path: str, chunk_size: int) -> Generator[list[bytes], None, None]:
    with open(path, "rb", buffering=16 * 1024 * 1024) as f:  # noqa: PTH123
        it = iter(f)
        yield from iter(lambda: list(islice(it, chunk_size)), [])


def _clean_temp_files(working_dir: Path) -> None:
    for temp_file in [
        *list(working_dir.glob("ctags-*.json")),
        *list(working_dir.glob("tmp*.json")),
    ]:
        try:
            temp_file.unlink()
        except OSError as e:
            LOGGER.warning("Failed to delete temporary file %s: %s", temp_file, e)


def _compute_language_value(language: Language) -> str:
    """Return the language string value compatible with ctags arguments."""
    if language == Language.JavaScript:
        return "JavaScript,+TypeScript"
    if language == Language.Go:
        return "Go"
    if language == Language.CSharp:
        return "C#"
    return str(language.value)


async def _ensure_index(open_client: AsyncOpenSearch, index_name: str) -> None:
    """Create the index if it does not exist."""
    if await open_client.indices.exists(index=index_name):
        return
    await open_client.indices.create(index=index_name, body={"settings": {"number_of_replicas": 1}})


async def _bulk_index_documents(
    *,
    client: AsyncOpenSearch,
    docs: list[dict[str, Any]],
    index_name: str,
) -> None:
    """Index documents using the bulk API."""
    bulk_lines = []
    for doc in docs:
        bulk_lines.append(
            orjson.dumps({"index": {"_index": index_name, "_id": str(doc["doc_id"])}}).decode(),
        )
        bulk_lines.append(orjson.dumps(doc).decode())

    bulk_body = "\n".join(bulk_lines) + "\n"
    await client.bulk(body=bulk_body, request_timeout=120)


def _attach_metadata(docs: list[dict[str, Any]], metadata: dict[str, str | None] | None) -> None:
    """Attach execution-level metadata to each document in place."""
    if not metadata:
        return
    for doc in docs:
        doc.setdefault("metadata", {}).update({k: v for k, v in metadata.items() if v is not None})


async def _consume_tags_file(  # noqa: PLR0913
    *,
    tags_path: str,
    loop: asyncio.AbstractEventLoop,
    executor: ProcessPoolExecutor,
    tiny_db: TinyDB,
    chunk_size: int,
    max_in_flight: int,
) -> None:
    """Stream-read the ctags json file and index/store the parsed documents."""
    semaphore = asyncio.Semaphore(max_in_flight)
    doc_counter = 0

    async def process_chunk(chunk: list[bytes]) -> None:
        nonlocal doc_counter
        async with semaphore:
            parsed = await loop.run_in_executor(executor, parse_chunk, chunk)
            if not parsed:
                return

            # Mirror into TinyDB
            tiny_db.insert_multiple(parsed)

    tasks = [
        asyncio.create_task(process_chunk(chunk)) for chunk in chunked_reader(tags_path, chunk_size)
    ]
    await asyncio.gather(*tasks)


async def create_tiny_db_from_ctags(  # noqa: PLR0913
    working_dir: Path,
    exclude: list[str] | None,
    language: Language,
    *,
    max_workers: int | None = None,
    chunk_size: int = 5000,
    max_in_flight: int = 4,
    metadata: dict[str, str | None] | None = None,
) -> tuple[TinyDB, str]:
    executor = ProcessPoolExecutor(max_workers=max_workers)
    loop = asyncio.get_running_loop()
    tags_output: str | None = None

    try:
        # Clean up any existing temporary files
        _clean_temp_files(working_dir)

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".json",
            dir=working_dir,
            prefix="ctags-",
        ) as tags_output_file:
            tags_output = tags_output_file.name

        language_value = _compute_language_value(language)

        args = [
            "--fields=+n+N+S",
            "--output-format=json",
            "--excmd=number",
            "-R",
            "--tag-relative=always",
            f"--languages=-all,+{language_value}",
            "-f",
            tags_output,
            *[f"--exclude={excl}" for excl in exclude or []],
            str(working_dir),
        ]

        process = await asyncio.create_subprocess_exec("ctags", *args)
        _, stderr = await process.communicate()
        await process.wait()

        if process.returncode != 0:
            LOGGER.error("ctags failed: %s", stderr.decode(errors="ignore"))
            return TinyDB(storage=MemoryStorage), ""
        if stderr:
            LOGGER.warning("ctags stderr: %s", stderr.decode(errors="ignore"))

        # TinyDB is still used by other parts of the codebase (e.g. orchestrator.py)
        # so we keep it for in-memory operations, but the **source of truth** will be
        # OpenSearch from now on.
        tiny_db = TinyDB(storage=MemoryStorage)

        # Decide the index name.  If a "uuid" was provided in metadata we use it to
        # create a unique index per execution, otherwise fall back to a generic one.
        index_name = (
            f"ctags-{metadata.get('uuid')}" if metadata and metadata.get("uuid") else "ctags-tags"
        )

        await _consume_tags_file(
            tags_path=tags_output,
            loop=loop,
            executor=executor,
            tiny_db=tiny_db,
            chunk_size=chunk_size,
            max_in_flight=max_in_flight,
        )

        return tiny_db, index_name

    finally:
        if tags_output and Path(tags_output).exists():
            Path(tags_output).unlink()
        executor.shutdown(wait=False)


def find_files(
    working_dir: str | Path,
    exclusions: list[Path] | None = None,
) -> list[Path]:
    working_dir = Path(working_dir)
    results = []
    exclusions = exclusions or []

    for root, dirs, files in os.walk(working_dir):
        root_path = Path(root)

        # Skip excluded directories
        dirs[:] = [d for d in dirs if not should_exclude(root_path / d, exclusions)]

        # Find files with matching extensions
        for file in files:
            file_path = root_path / file

            if not should_exclude(file_path, exclusions):
                results.append(file_path.absolute())

    return results


def parse_chunk(lines: list[bytes]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            parsed = orjson.loads(line)
            # if not is_dependency_file(Path(parsed["path"])):
            out.append(parsed)
        except orjson.JSONDecodeError:
            LOGGER.debug("Skipping invalid JSON line: %r", line[:50])
    return out
