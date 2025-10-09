import logging
from pathlib import Path
from typing import BinaryIO, Iterator, NoReturn

from minio import Minio
from minio.error import S3Error

from toolkit.exceptions import (
    MinioBucketNotFound,
    MinioObjectNotFound,
    ProgrammingError,
    ServerError,
    registry,
)
from toolkit.exceptions.registry import ExceptionNotFound

logger = logging.getLogger(__name__)


class MinioClient(object):
    client: Minio
    bucket: str
    base_path: str | None
    minio_url: str
    proxy_url: str | None
    default_part_size: int = 10 * 1024 * 1024

    def __init__(
        self,
        url: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        base_path: str | None = None,
        proxy_url: str | None = None,
        secure: bool = True,
    ):
        logger.debug(f"Making new MinIO service client for url={url} bucket={bucket}.")
        self.minio_url = self.get_url_without_protocol(url)
        self.bucket = bucket
        if base_path and base_path.endswith("/"):
            self.base_path = base_path[:-1]
        else:
            self.base_path = base_path
        if proxy_url:
            self.proxy_url = self.get_url_without_protocol(proxy_url)
        else:
            self.proxy_url = None

        try:
            self.client = Minio(
                self.minio_url,  # this accepts only URLs without protocol
                access_key=access_key,
                secret_key=secret_key,
                region="us-east-1",  # this is the region of our minio server at minio81.iiasa.ac.at:9000
                secure=secure,
            )
            if not self.client.bucket_exists(self.bucket):
                raise MinioBucketNotFound()
        except S3Error as e:
            self.raise_exception(e)

    def get_file(self, path: str, target_file: str | Path) -> None:
        if isinstance(target_file, Path):
            target_file = str(target_file)
        object_name = self.get_object_name(path)
        try:
            self.client.fget_object(self.bucket, object_name, str(target_file))
        except S3Error as e:
            self.raise_exception(e)

    def get_file_stream(self, path: str) -> Iterator[bytes]:
        object_name = self.get_object_name(path)
        try:
            response = self.client.get_object(self.bucket, object_name)
            yield response.read()
        except S3Error as e:
            self.raise_exception(e)
        response.close()

    def put_file(self, path: str, source_file: str | Path) -> None:
        if (isinstance(source_file, Path) and not source_file.exists()) or (
            isinstance(source_file, str) and not Path(source_file).exists()
        ):
            raise ProgrammingError(f"File {source_file} does not exist.")
        if isinstance(source_file, Path):
            source_file = str(source_file)
        object_name = self.get_object_name(path)

        try:
            self.client.fput_object(self.bucket, object_name, source_file)
        except S3Error as e:
            self.raise_exception(e)

    def put_file_stream(
        self, path: str, stream: BinaryIO, size: int | None = None
    ) -> None:
        object_name = self.get_object_name(path)
        try:
            if size is None:
                self.client.put_object(
                    self.bucket,
                    object_name,
                    stream,
                    -1,
                    part_size=self.default_part_size,
                )
            else:
                self.client.put_object(self.bucket, object_name, stream, size)
        except S3Error as e:
            self.raise_exception(e)

    def delete_file(self, path: str) -> None:
        try:
            # remove_object does not throw an exception if the object does not exist, so fetch object information first
            self.client.stat_object(self.bucket, path)
            self.client.remove_object(self.bucket, path)
        except S3Error as e:
            self.raise_exception(e)

    def get_upload_url(self, path: str) -> str:
        object_name = self.get_object_name(path)
        # this does not throw an exception if the object or bucket does not exist
        url = self.client.presigned_put_object(self.bucket, object_name)
        return self.get_proxied_url(url)

    def get_download_url(self, path: str) -> str:
        object_name = self.get_object_name(path)
        # this does not throw an exception if the object or bucket does not exist
        url = self.client.presigned_get_object(self.bucket, object_name)
        return self.get_proxied_url(url)

    def get_full_path(self, path: str) -> str:
        object_name = self.get_object_name(path)
        return f"{self.bucket}/{object_name}"

    def get_object_name(self, path: str) -> str:
        if self.base_path:
            return f"{self.base_path}/{path}"
        return path

    def get_url_without_protocol(self, url: str) -> str:
        if url.startswith("https://"):
            return url[8:]
        elif url.startswith("http://"):
            return url[7:]
        return url

    def get_proxied_url(self, url: str) -> str:
        if not self.proxy_url:
            return url
        else:
            return url.replace(self.minio_url, self.proxy_url)

    def raise_exception(self, e: S3Error) -> NoReturn:
        try:
            if e.code == "NoSuchBucket" or e.code == "AccessDenied":
                raise MinioBucketNotFound() from e
            elif e.code == "NoSuchKey":
                raise MinioObjectNotFound() from e
            else:
                raise registry.exception_from_status_code(e.response.status, e.code)
        except ExceptionNotFound:
            raise ServerError(
                http_error_name=e.code, http_status_code=e.response.status
            )
