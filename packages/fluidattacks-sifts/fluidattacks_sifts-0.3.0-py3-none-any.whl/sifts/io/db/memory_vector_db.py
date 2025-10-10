import logging
import shutil
import tarfile
from datetime import datetime
from pathlib import Path

import aiofiles
from platformdirs import user_data_dir

from sifts.io.aws import (
    FileDownloadError,
    download_from_s3,
    get_s3_object_last_modified,
)
from sifts.io.tar import safe_extract_tar

MATCHES_BUCKET = "fluidattacks-matches"
_DB_REMOTE_PATH = "defines_embeddings/"
_BASE_DIR = user_data_dir(appname="sifts", appauthor="fluidattacks", ensure_exists=True)
_LOCAL_DB_METADATA_DIR = Path(_BASE_DIR, "embeddings")
LOGGER = logging.getLogger(__name__)


async def _fetch_meta() -> None:
    archive_name = "embeddings.tar.gz"
    download_target_path = Path(_BASE_DIR, archive_name)
    info_file_path = download_target_path.with_suffix(download_target_path.suffix + ".info")
    must_download = False
    last_modified_time_remote = await get_s3_object_last_modified(
        bucket=MATCHES_BUCKET,
        object_key=f"{_DB_REMOTE_PATH}{archive_name}",
    )
    if info_file_path.exists():
        async with aiofiles.open(info_file_path) as f:
            last_modified_time = datetime.fromisoformat(await f.read())
        if last_modified_time_remote > last_modified_time:
            LOGGER.info("Remote db object is newer than local. Downloading new instance.")
            must_download = True
    else:
        must_download = True
    try:
        if must_download:
            await download_from_s3(
                bucket=MATCHES_BUCKET,
                object_key=f"{_DB_REMOTE_PATH}{archive_name}",
                download_path=download_target_path,
            )
            if download_target_path.exists():
                shutil.rmtree(_LOCAL_DB_METADATA_DIR, ignore_errors=True)
                LOGGER.info("Extracting %s to %s", archive_name, _BASE_DIR)
                with tarfile.open(download_target_path, "r:gz") as tar:
                    await safe_extract_tar(tar, Path(_BASE_DIR))

                async with aiofiles.open(info_file_path, "w") as f:
                    await f.write(str(last_modified_time_remote.isoformat()))
            else:
                LOGGER.error("Failed to download %s", archive_name)
    except FileDownloadError:
        LOGGER.info("Remote db object not found. A new instance will be created on post action.")
    finally:
        download_target_path.unlink(missing_ok=True)
