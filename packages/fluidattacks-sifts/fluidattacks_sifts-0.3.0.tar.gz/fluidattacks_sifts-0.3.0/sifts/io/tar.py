import asyncio
import logging
import tarfile
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def _is_member_safe(
    member: tarfile.TarInfo,
    max_size: int,
) -> bool:
    return not (
        member.issym()
        or member.islnk()
        or Path(member.name).is_absolute()
        or "../" in member.name
        or member.size > max_size
    )


async def safe_extract_tar(
    tar_handler: tarfile.TarFile,
    file_path: Path,
    max_size_mgs: int = 512,
) -> None:
    one_meg = 1024 * 1024
    for member in tar_handler.getmembers():
        if not _is_member_safe(member, max_size_mgs * one_meg):
            LOGGER.error("Unsafe path detected: %s", member.name)
            continue
        await asyncio.to_thread(tar_handler.extract, member, path=file_path, numeric_owner=True)
        LOGGER.info("Extracted: %s", member.name)
