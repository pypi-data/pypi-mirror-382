"""High-level entrypoints for the ModelRed Python SDK.

These clients compose the shared transports, authentication helpers, and
resource-specific service objects introduced in the refactor. They provide a
stable surface for consumers while ensuring API keys are validated centrally
and never generated from within the SDK.
"""

from __future__ import annotations

from typing import Mapping, Optional

try:  # pragma: no cover - best effort metadata lookup
    from importlib import metadata as importlib_metadata
except ImportError:  # pragma: no cover - Python < 3.8 fallback
    import importlib_metadata  # type: ignore

from .auth import build_auth_headers, resolve_api_key, redact_api_key
from .config import SDKSettings, USER_AGENT_TEMPLATE, load_settings
from .http import AsyncHTTPTransport, SyncHTTPTransport
from .resources.assessments import AssessmentsClient, AsyncAssessmentsClient
from .resources.models import ModelsClient, AsyncModelsClient
from .resources.probes import ProbesClient, AsyncProbesClient


def _default_user_agent() -> str:
    try:
        version = importlib_metadata.version("modelred")
    except Exception:  # pragma: no cover - fallback when package metadata absent
        version = "dev"
    return USER_AGENT_TEMPLATE.format(version=version)


class ModelRedClient:
    """Synchronous top-level client that exposes resource helpers."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        organization_id: Optional[str] = None,
        settings: Optional[SDKSettings] = None,
        transport: Optional[SyncHTTPTransport] = None,
        user_agent: Optional[str] = None,
        additional_headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        self._api_key = resolve_api_key(api_key)
        self._organization_id = organization_id
        self._settings = settings or load_settings()

        if transport is None:
            self._transport = SyncHTTPTransport(
                base_url=self._settings.base_url,
                timeout=self._settings.timeout,
                max_retries=self._settings.max_retries,
                retry_backoff=self._settings.retry_backoff,
            )
            self._owns_transport = True
        else:
            self._transport = transport
            self._owns_transport = False

        base_headers = build_auth_headers(
            self._api_key, organization_id=organization_id
        )
        base_headers.setdefault("User-Agent", user_agent or _default_user_agent())
        if additional_headers:
            # Caller-provided headers win over defaults
            base_headers.update(additional_headers)

        self.models = ModelsClient(self._transport, base_headers)
        self.assessments = AssessmentsClient(self._transport, base_headers)
        self.probes = ProbesClient(self._transport, base_headers)

    @property
    def settings(self) -> SDKSettings:
        return self._settings

    @property
    def api_key(self) -> str:
        return self._api_key

    def redacted_api_key(self) -> str:
        return redact_api_key(self._api_key)

    def close(self) -> None:
        if self._owns_transport:
            self._transport.close()

    def __enter__(self) -> "ModelRedClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


class AsyncModelRedClient:
    """Async top-level client that exposes resource helpers."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        organization_id: Optional[str] = None,
        settings: Optional[SDKSettings] = None,
        transport: Optional[AsyncHTTPTransport] = None,
        user_agent: Optional[str] = None,
        additional_headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        self._api_key = resolve_api_key(api_key)
        self._organization_id = organization_id
        self._settings = settings or load_settings()

        if transport is None:
            self._transport = AsyncHTTPTransport(
                base_url=self._settings.base_url,
                timeout=self._settings.timeout,
                max_retries=self._settings.max_retries,
                retry_backoff=self._settings.retry_backoff,
            )
            self._owns_transport = True
        else:
            self._transport = transport
            self._owns_transport = False

        base_headers = build_auth_headers(
            self._api_key, organization_id=organization_id
        )
        base_headers.setdefault("User-Agent", user_agent or _default_user_agent())
        if additional_headers:
            base_headers.update(additional_headers)

        self.models = AsyncModelsClient(self._transport, base_headers)
        self.assessments = AsyncAssessmentsClient(self._transport, base_headers)
        self.probes = AsyncProbesClient(self._transport, base_headers)

    @property
    def settings(self) -> SDKSettings:
        return self._settings

    @property
    def api_key(self) -> str:
        return self._api_key

    def redacted_api_key(self) -> str:
        return redact_api_key(self._api_key)

    async def close(self) -> None:
        if self._owns_transport:
            await self._transport.close()

    async def __aenter__(self) -> "AsyncModelRedClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()


__all__ = [
    "ModelRedClient",
    "AsyncModelRedClient",
]
