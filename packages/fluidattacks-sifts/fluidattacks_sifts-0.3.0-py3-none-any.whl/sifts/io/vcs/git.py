import asyncio
from pathlib import Path


async def get_last_commit(repo_path: Path | str) -> str:
    process = await asyncio.create_subprocess_exec(
        "git",
        "rev-parse",
        "HEAD",
        cwd=repo_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await process.communicate()
    return stdout.decode().strip()


async def get_repo_top_level(repo_path: Path) -> Path:
    process = await asyncio.create_subprocess_exec(
        "git",
        "rev-parse",
        "--show-toplevel",
        cwd=repo_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await process.communicate()
    return Path(stdout.decode().strip())


async def get_last_commit_file(repo_path: Path, file_path: Path) -> str:
    process = await asyncio.create_subprocess_exec(
        "git",
        "log",
        "-1",
        "--format=%H",
        "--",
        str(file_path),
        cwd=repo_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await process.communicate()
    return stdout.decode().strip()
