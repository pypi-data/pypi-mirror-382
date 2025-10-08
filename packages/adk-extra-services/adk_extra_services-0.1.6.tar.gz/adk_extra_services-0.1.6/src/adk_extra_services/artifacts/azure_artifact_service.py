"""Azure Blob Storage artifact service implementation for Google ADK."""

from __future__ import annotations

import logging
from typing import Any, Optional

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    ContentSettings,
)
from google.adk.artifacts import BaseArtifactService
from google.genai import types
from typing_extensions import override

logger = logging.getLogger("adk_extra_services.artifacts.azure_blob")


class AzureBlobArtifactService(BaseArtifactService):
    """An artifact service implementation using Azure Blob Storage."""

    def __init__(
        self,
        *,
        container_name: str,
        # Choose ONE of the two ways to authenticate:
        connection_string: Optional[str] = None,
        account_url: Optional[
            str
        ] = None,  # e.g. "https://<account>.blob.core.windows.net"
        credential: Optional[
            object
        ] = None,  # e.g. DefaultAzureCredential, SAS token, account key
        ensure_container: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            container_name: Target container for artifacts.
            connection_string: If provided, used to create the client.
            account_url: If using URL-based auth, provide account URL.
            credential: Credential object or token string (SAS, key, etc.).
            ensure_container: Create container if it doesn't exist.
            **kwargs: Reserved for future compatibility.
        """
        if connection_string:
            self._service = BlobServiceClient.from_connection_string(
                connection_string, **kwargs
            )
        elif account_url:
            self._service = BlobServiceClient(
                account_url=account_url, credential=credential, **kwargs
            )
        else:
            raise ValueError(
                "Provide either 'connection_string' or ('account_url' + 'credential')."
            )

        self.container_name = container_name
        self.container: ContainerClient = self._service.get_container_client(
            container_name
        )

        if ensure_container:
            try:
                self.container.create_container()
            except ResourceExistsError:
                # Already exists
                pass
            except Exception as e:
                raise ("Could not ensure container %r: %s", container_name, e)

    # ---------- helpers ----------

    def _file_has_user_namespace(self, filename: str) -> bool:
        return filename.startswith("user:")

    def _blob_name(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
        version: int,
    ) -> str:
        # Keep parity with S3 implementation: if filename has 'user:', don't strip it;
        # paths store whatever is passed as <filename>.
        if self._file_has_user_namespace(filename):
            return f"{app_name}/{user_id}/user/{filename}/{version}"
        return f"{app_name}/{user_id}/{session_id}/{filename}/{version}"

    def _prefix_for_filename(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
    ) -> str:
        if self._file_has_user_namespace(filename):
            return f"{app_name}/{user_id}/user/{filename}/"
        return f"{app_name}/{user_id}/{session_id}/{filename}/"

    # ---------- BaseArtifactService API ----------

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
        # Determine next version
        versions = await self.list_versions(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            filename=filename,
        )
        version = 0 if not versions else max(versions) + 1

        blob_name = self._blob_name(app_name, user_id, session_id, filename, version)
        blob_client = self.container.get_blob_client(blob_name)

        content_type = (
            getattr(artifact.inline_data, "mime_type", None)
            or "application/octet-stream"
        )
        data = artifact.inline_data.data

        blob_client.upload_blob(
            data,
            overwrite=False,  # new version = new blob name
            content_settings=ContentSettings(content_type=content_type),
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
        # If version not specified, load latest
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

        blob_name = self._blob_name(app_name, user_id, session_id, filename, version)
        blob_client = self.container.get_blob_client(blob_name)

        try:
            # Fetch properties first to get content type (faster than reading then getting props)
            props = blob_client.get_blob_properties()
            content_type = (
                props.content_settings.content_type
                if props
                and props.content_settings
                and props.content_settings.content_type
                else "application/octet-stream"
            )

            stream = blob_client.download_blob()
            data = stream.readall()
        except ResourceNotFoundError:
            return None

        return types.Part.from_bytes(data=data, mime_type=content_type)

    @override
    async def list_artifact_keys(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> list[str]:
        """
        Return distinct artifact filenames visible to the caller, combining
        session-scoped and user-scoped objects. Mirrors S3 implementation behavior.
        """
        filenames: set[str] = set()

        # Session-scoped
        session_prefix = f"{app_name}/{user_id}/{session_id}/"
        for blob in self.container.list_blobs(name_starts_with=session_prefix):
            # <app>/<user>/<session>/<filename>/<version>
            parts = blob.name.split("/")
            if len(parts) >= 5:
                filenames.add(parts[3])

        # User-scoped
        user_prefix = f"{app_name}/{user_id}/user/"
        for blob in self.container.list_blobs(name_starts_with=user_prefix):
            # <app>/<user>/user/<filename>/<version>
            parts = blob.name.split("/")
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
            blob_name = self._blob_name(app_name, user_id, session_id, filename, ver)
            try:
                self.container.delete_blob(blob_name)
            except ResourceNotFoundError:
                # Already gone; ignore
                pass

    @override
    async def list_versions(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        filename: str,
    ) -> list[int]:
        """
        Lists versions by enumerating blobs under the filename prefix and
        parsing the final path segment as an int.
        """
        prefix = self._prefix_for_filename(app_name, user_id, session_id, filename)
        versions: list[int] = []
        try:
            for blob in self.container.list_blobs(name_starts_with=prefix):
                # Expect keys like: .../<filename>/<version>
                name = blob.name.rstrip("/")
                parts = name.split("/")
                if not parts:
                    continue
                ver_str = parts[-1]
                try:
                    versions.append(int(ver_str))
                except ValueError:
                    # Ignore non-numeric terminal segments
                    continue
        except ResourceNotFoundError:
            # Container missing or path empty – treat as no versions
            return []

        return sorted(versions)
