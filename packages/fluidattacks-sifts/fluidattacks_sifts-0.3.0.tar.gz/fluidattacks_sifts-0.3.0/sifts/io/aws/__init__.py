from datetime import datetime
from pathlib import Path

import aioboto3
from botocore.exceptions import ClientError

SESSION = aioboto3.Session()


class FileDownloadError(Exception):
    def __init__(self, object_key: str, bucket: str) -> None:
        self.object_key = object_key
        self.bucket = bucket
        message = f"Error downloading file {object_key} from bucket {bucket}"
        super().__init__(message)


class S3ObjectNotFoundError(Exception):
    def __init__(
        self,
        object_key: str,
        bucket: str,
        *,
        is_not_found_case: bool = True,
    ) -> None:
        self.object_key = object_key
        self.bucket = bucket
        if is_not_found_case:
            message = f"Object {object_key} not found in bucket {bucket}"
        else:
            message = f"Error accessing object metadata for {object_key} in bucket {bucket}"
        super().__init__(message)


async def download_from_s3(bucket: str, object_key: str, download_path: Path) -> None:
    try:
        async with SESSION.client("s3") as s3_client:
            await s3_client.download_file(bucket, object_key, str(download_path))
    except ClientError as exc:
        raise FileDownloadError(object_key, bucket) from exc


async def get_s3_object_last_modified(bucket: str, object_key: str) -> datetime:
    try:
        async with SESSION.client("s3") as s3_client:
            response = await s3_client.head_object(Bucket=bucket, Key=object_key)
            last_modified = response["LastModified"]
            if not isinstance(last_modified, datetime):
                message = f"Expected datetime object for LastModified, got {type(last_modified)}"
                raise TypeError(message)
            return last_modified
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "404":
            raise S3ObjectNotFoundError(object_key, bucket, is_not_found_case=True) from exc

        raise S3ObjectNotFoundError(object_key, bucket, is_not_found_case=False) from exc
