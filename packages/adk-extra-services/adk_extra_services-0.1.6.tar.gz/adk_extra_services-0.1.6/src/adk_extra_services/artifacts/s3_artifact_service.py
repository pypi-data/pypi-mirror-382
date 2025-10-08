"""S3 artifact service implementation for Google ADK."""

import logging
from typing import Optional

import boto3
from google.adk.artifacts import BaseArtifactService
from google.genai import types
from typing_extensions import override

logger = logging.getLogger("adk_extra_services.artifacts.s3")


class S3ArtifactService(BaseArtifactService):
    """An artifact service implementation using AWS S3 or S3-compatible storage."""

    def __init__(
        self,
        bucket_name: str,
        endpoint_url: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region_name: Optional[str] = None,
        **kwargs,
    ):
        """Initializes the S3ArtifactService.

        Args:
            bucket_name: The name of the S3 bucket.
            endpoint_url: Optional endpoint URL for S3-compatible storage (e.g., MinIO).
            aws_access_key_id: Optional AWS access key. Uses environment/config if not provided.
            aws_secret_access_key: Optional AWS secret key. Uses environment/config if not provided.
            region_name: Optional AWS region. Uses environment/config if not provided.
            **kwargs: Additional keyword arguments to pass to boto3.client('s3').
        """
        self.bucket_name = bucket_name

        # Prepare S3 client configuration
        client_kwargs = kwargs.copy()
        if endpoint_url:
            client_kwargs["endpoint_url"] = endpoint_url
        if aws_access_key_id:
            client_kwargs["aws_access_key_id"] = aws_access_key_id
        if aws_secret_access_key:
            client_kwargs["aws_secret_access_key"] = aws_secret_access_key
        if region_name:
            client_kwargs["region_name"] = region_name

        self.s3_client = boto3.client("s3", **client_kwargs)

    def _file_has_user_namespace(self, filename: str) -> bool:
        return filename.startswith("user:")

    def _get_object_key(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
        version: int,
    ) -> str:
        if self._file_has_user_namespace(filename):
            return f"{app_name}/{user_id}/user/{filename}/{version}"
        return f"{app_name}/{user_id}/{session_id}/{filename}/{version}"

    @override
    async def save_artifact(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
        artifact: types.Part,
    ) -> int:
        versions = await self.list_versions(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            filename=filename,
        )
        version = 0 if not versions else max(versions) + 1

        key = self._get_object_key(app_name, user_id, session_id, filename, version)
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=artifact.inline_data.data,
            ContentType=artifact.inline_data.mime_type,
        )
        return version

    @override
    async def load_artifact(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
        version: Optional[int] = None,
    ) -> Optional[types.Part]:
        if version is None:
            versions = await self.list_versions(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id,
                filename=filename,
            )
            if not versions:
                return None
            version = max(versions)

        key = self._get_object_key(app_name, user_id, session_id, filename, version)
        try:
            resp = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            data = resp["Body"].read()
            mime = resp.get("ContentType")
        except self.s3_client.exceptions.NoSuchKey:
            return None

        return types.Part.from_bytes(data=data, mime_type=mime)

    @override
    async def list_artifact_keys(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> list[str]:
        filenames = set()

        session_prefix = f"{app_name}/{user_id}/{session_id}/"
        paginator = self.s3_client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket_name, Prefix=session_prefix):
            for obj in page.get("Contents", []):
                parts = obj["Key"].split("/")
                if len(parts) >= 5:
                    filenames.add(parts[3])

        user_prefix = f"{app_name}/{user_id}/user/"
        for page in paginator.paginate(Bucket=self.bucket_name, Prefix=user_prefix):
            for obj in page.get("Contents", []):
                parts = obj["Key"].split("/")
                if len(parts) >= 5:
                    filenames.add(parts[3])

        return sorted(filenames)

    @override
    async def delete_artifact(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
    ) -> None:
        versions = await self.list_versions(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            filename=filename,
        )
        for ver in versions:
            key = self._get_object_key(app_name, user_id, session_id, filename, ver)
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)

    @override
    async def list_versions(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
    ) -> list[int]:
        if self._file_has_user_namespace(filename):
            prefix = f"{app_name}/{user_id}/user/{filename}/"
        else:
            prefix = f"{app_name}/{user_id}/{session_id}/{filename}/"
        versions = []
        paginator = self.s3_client.get_paginator("list_objects_v2")
        try:
            for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
                for obj in page.get("Contents", []):
                    parts = obj["Key"].rstrip("/").split("/")
                    ver_str = parts[-1]
                    try:
                        versions.append(int(ver_str))
                    except ValueError:
                        continue
        except self.s3_client.exceptions.NoSuchKey:
            # Happens when prefix does not yet exist in the bucket. Treat as no versions.
            return []
        except self.s3_client.exceptions.NoSuchBucket:
            logger.error("Bucket %s does not exist", self.bucket_name)
            raise

        return versions
