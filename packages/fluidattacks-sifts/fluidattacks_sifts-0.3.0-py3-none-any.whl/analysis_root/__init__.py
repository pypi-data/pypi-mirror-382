import argparse
import asyncio
import json
import logging
from contextlib import suppress
from pathlib import Path

import aioboto3
import aiofiles
from platformdirs import user_data_dir

from sifts.analysis.orchestrator import scan_projects
from sifts.config import AnalysisConfig, ExecutionContext, SiftsConfig
from sifts.core.sarif_result import get_sarif
from sifts.io.api import fetch_group_roots, initialize_session

_BASE_DIR = user_data_dir(appname="sifts", appauthor="fluidattacks", ensure_exists=True)


LOGGER = logging.getLogger(__name__)


async def run_cli(group_name: str, nickname: str, output_path: Path) -> None:
    session = aioboto3.Session()
    integrates_session, _ = initialize_session()
    data = await fetch_group_roots(integrates_session, group_name)
    root_id = next(
        (x["id"] for x in data["data"]["group"]["roots"] if x["nickname"] == nickname),
        None,
    )
    results_db_path = Path(_BASE_DIR, f"{group_name}_{nickname}.db")

    if not root_id:
        LOGGER.error("Root ID not found")
        return
    async with session.client("s3") as s3_client:
        with suppress(s3_client.exceptions.ClientError):
            await s3_client.download_file(
                "machine.data",
                f"smells/{group_name}/{nickname}/result.db",
                str(results_db_path),
            )

    Path(_BASE_DIR, "groups").mkdir(parents=True, exist_ok=True)
    process = await asyncio.create_subprocess_exec(
        "melts",
        "pull-repos",
        "--group",
        group_name,
        "--root",
        nickname,
        cwd=_BASE_DIR,
    )
    await process.wait()
    if process.returncode != 0:
        LOGGER.error("Failed to pull repos")
        return
    working_dir = Path(_BASE_DIR, "groups", group_name, nickname)
    if not working_dir.exists():
        LOGGER.warning("Working directory not found")
        return
    valid_vulnerabilities: list[str] = [
        "016",
        "022",
        "031",
        "037",
        "238",
        "263",
        "264",
        "282",
        "313",
        "325",
        "350",
        "362",
        "372",
        "385",
    ]
    with suppress(ValueError):
        config = SiftsConfig(
            context=ExecutionContext(
                root_id=root_id,
                group_name=group_name,
                root_nickname=nickname,
            ),
            analysis=AnalysisConfig(
                working_dir=working_dir,
                split_subdirectories=False,
                enable_navigation=True,
                include_vulnerabilities=valid_vulnerabilities,
                model="gpt-4.1-mini",
            ),
            results_db_path=Path(_BASE_DIR, f"{group_name}_{nickname}.db"),
        )
        result = await scan_projects(config)
        sarif = await get_sarif(result, config)
        async with aiofiles.open(output_path, "w") as f:
            await f.write(json.dumps(sarif, indent=2))

    bucket_name = "machine.data"
    key_name = f"smells/{group_name}/{nickname}/result.json"

    async with session.client("s3") as s3_client:
        try:
            await s3_client.upload_file(
                str(results_db_path),
                bucket_name,
                f"smells/{group_name}/{nickname}/result.db",
            )
            await s3_client.upload_file(str(output_path), bucket_name, key_name)
        except s3_client.exceptions.ClientError:
            LOGGER.exception("Failed to upload results to S3")


async def main() -> None:
    parser = argparse.ArgumentParser(description="CLI for sifts analysis.")
    parser.add_argument("group_name", help="Name of the group")
    parser.add_argument("nickname", help="Nickname of the root")
    parser.add_argument(
        "output_path",
        nargs="?",
        help="Path to output SARIF file",
        default="sarif.json",
    )
    args = parser.parse_args()
    await run_cli(args.group_name, args.nickname, Path(args.output_path).resolve())


def main_cli() -> None:
    asyncio.run(main())
