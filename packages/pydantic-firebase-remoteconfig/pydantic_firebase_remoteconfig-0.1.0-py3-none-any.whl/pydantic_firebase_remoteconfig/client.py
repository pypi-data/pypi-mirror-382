from enum import StrEnum
from typing import Any

from httpx import AsyncClient
from google.auth import default
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request

DEFAULT_API_ENDPOINT = "https://firebaseremoteconfig.googleapis.com"


class FirebaseNamespace(StrEnum):
    FIREBASE = "firebase"
    FIREBASE_SERVER = "firebase-server"


class FirebaseRemoteConfigClient:
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

    async def get_server_remote_template(self) -> dict[str, Any]:
        endpoint = f"/v1/projects/{self._project}/namespaces/{FirebaseNamespace.FIREBASE_SERVER.value}/remoteConfig"
        response = await self._transport.get(endpoint)
        response.raise_for_status()
        template = response.json()
        if not isinstance(template, dict):
            raise ValueError(f"Invalid response from Firebase: {template}")
        return template
