"""Shared base classes for resource-specific API clients."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from ..http import RequestOptions, SyncHTTPTransport, AsyncHTTPTransport


class SyncAPIResource:
    """Convenience wrapper that provides a merged-header request helper."""

    def __init__(
        self,
        transport: SyncHTTPTransport,
        base_headers: Mapping[str, str],
    ) -> None:
        self._transport = transport
        self._base_headers = dict(base_headers)

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Any = None,
        options: Optional[RequestOptions] = None,
    ) -> dict[str, Any]:
        headers = dict(self._base_headers)
        return self._transport.request(
            method,
            path,
            params=params,
            json=json,
            headers=headers,
            options=options,
        )


class AsyncAPIResource:
    """Asynchronous counterpart to :class:`SyncAPIResource`."""

    def __init__(
        self,
        transport: AsyncHTTPTransport,
        base_headers: Mapping[str, str],
    ) -> None:
        self._transport = transport
        self._base_headers = dict(base_headers)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Any = None,
        options: Optional[RequestOptions] = None,
    ) -> dict[str, Any]:
        headers = dict(self._base_headers)
        return await self._transport.request(
            method,
            path,
            params=params,
            json=json,
            headers=headers,
            options=options,
        )
