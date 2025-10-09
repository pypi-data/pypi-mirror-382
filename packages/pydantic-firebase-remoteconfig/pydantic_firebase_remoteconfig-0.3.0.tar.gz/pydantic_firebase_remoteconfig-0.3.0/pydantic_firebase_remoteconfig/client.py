from enum import StrEnum
from typing import Any

from httpx import AsyncClient
from google.auth import default
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from pydantic_core import to_json

DEFAULT_API_ENDPOINT = "https://firebaseremoteconfig.googleapis.com"


class FirebaseNamespace(StrEnum):
    FIREBASE = "firebase"
    FIREBASE_SERVER = "firebase-server"


class FirebaseRemoteConfigClient:
    @classmethod
    def from_credentials(
        cls,
        credentials: Credentials,
        project: str,
    ) -> "FirebaseRemoteConfigClient":
        headers: dict[str, str] = dict()
        if not credentials.valid:
            credentials.refresh(Request())  # type: ignore
            credentials.apply(headers)  # type: ignore
        transport = AsyncClient(
            base_url=DEFAULT_API_ENDPOINT,
            headers=headers,
        )
        return cls(project, transport)

    @classmethod
    def from_environment(cls) -> "FirebaseRemoteConfigClient":
        credentials: Credentials
        project: str
        headers: dict[str, str] = dict()
        credentials, project = default()  # type: ignore
        credentials.refresh(Request())  # type: ignore
        credentials.apply(headers)  # type: ignore
        transport = AsyncClient(
            base_url=DEFAULT_API_ENDPOINT,
            headers=headers,
        )
        return cls(project, transport)

    def __init__(
        self,
        project: str,
        transport: AsyncClient,
    ) -> None:
        self._project = project
        self._transport = transport

    @property
    def project(self) -> str:
        return self._project

    async def get_server_remote_template(self) -> tuple[dict[str, Any], str]:
        endpoint = f"/v1/projects/{self._project}/namespaces/{FirebaseNamespace.FIREBASE_SERVER.value}/remoteConfig"
        response = await self._transport.get(endpoint)
        response.raise_for_status()
        etag = response.headers.get("ETag")
        template = response.json()
        if not isinstance(template, dict):
            raise ValueError(f"Invalid response from Firebase: {template}")
        return template, etag

    async def update_server_remote_template(
        self,
        template: bytes | dict[str, Any] | str,
        *,
        etag: str | None = None,
    ) -> None:
        endpoint = f"/v1/projects/{self._project}/namespaces/{FirebaseNamespace.FIREBASE_SERVER.value}/remoteConfig"
        headers = dict()
        if etag is not None:
            headers.update(
                {
                    "If-Match": etag,
                },
            )
        if isinstance(template, dict):
            template = to_json(template)
        response = await self._transport.put(
            endpoint,
            headers=headers,
            content=template,
        )
        response.raise_for_status()
