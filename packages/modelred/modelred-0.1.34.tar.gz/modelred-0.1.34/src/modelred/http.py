"""HTTP transport utilities for the ModelRed Python SDK.

This module will eventually contain the shared synchronous and asynchronous
request execution logic, including retry/backoff behaviour, telemetry, and
instrumentation hooks. For now, it provides lightweight abstractions that the
higher-level clients can depend on without altering existing behaviour.
"""

from __future__ import annotations

import asyncio
import json
import random
import time
from dataclasses import dataclass
from typing import Any, Mapping, Optional
from urllib.parse import urljoin

try:  # pragma: no cover - import guard for optional deps during type checking
    import aiohttp  # type: ignore
except ImportError as _aiohttp_error:  # pragma: no cover
    aiohttp = None  # type: ignore

try:  # pragma: no cover
    import requests  # type: ignore
except ImportError as _requests_error:  # pragma: no cover
    requests = None  # type: ignore

from .config import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_BACKOFF,
    DEFAULT_TIMEOUT,
)
from .exceptions import NetworkError, raise_for_status

_ASYNC_PARSE_ERRORS: tuple[type[BaseException], ...]
if aiohttp is not None:
    _ASYNC_PARSE_ERRORS = (aiohttp.ContentTypeError, json.JSONDecodeError)
    _AIOHTTP_CLIENT_ERROR = aiohttp.ClientError
else:
    _ASYNC_PARSE_ERRORS = (json.JSONDecodeError,)

    class _AIOHTTPClientErrorFallback(Exception):
        """Fallback error used when aiohttp is not installed."""

        pass

    _AIOHTTP_CLIENT_ERROR = _AIOHTTPClientErrorFallback


@dataclass(slots=True)
class RequestOptions:
    """Container for request-level overrides."""

    timeout: Optional[float] = None
    base_url: Optional[str] = None
    headers: Optional[Mapping[str, str]] = None


def _build_url(base_url: str, path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if not path.startswith("/"):
        path = f"/{path}"
    return urljoin(f"{base_url.rstrip('/')}/", path.lstrip("/"))


def _should_retry(status: int) -> bool:
    return status >= 500 or status == 429


def _parse_response(resp: Any) -> dict[str, Any]:
    try:
        payload = resp.json()
        if isinstance(payload, dict):
            return payload
        return {"data": payload}
    except json.JSONDecodeError:
        return {"error": resp.text}


async def _parse_async_response(resp: Any) -> dict[str, Any]:
    try:
        payload = await resp.json()
        if isinstance(payload, dict):
            return payload
        return {"data": payload}
    except _ASYNC_PARSE_ERRORS:
        text = await resp.text()
        return {"error": text}


class SyncHTTPTransport:
    """Thin wrapper around :mod:`requests` with retry/backoff support."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_backoff: float = DEFAULT_RETRY_BACKOFF,
        session: Optional[Any] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max(0, max_retries)
        self._retry_backoff = max(0.0, retry_backoff)
        if requests is None:
            raise RuntimeError(
                "The 'requests' package is required for synchronous HTTP transport"
            ) from _requests_error
        self._session = session or requests.Session()  # type: ignore[call-arg]

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Any = None,
        headers: Optional[Mapping[str, str]] = None,
        options: Optional[RequestOptions] = None,
    ) -> dict[str, Any]:
        opts = options or RequestOptions()
        timeout = opts.timeout if opts.timeout is not None else self._timeout
        base_url = opts.base_url or self._base_url
        url = _build_url(base_url, path)

        combined_headers: dict[str, str] = {}
        if headers:
            combined_headers.update(headers)
        if opts.headers:
            combined_headers.update(opts.headers)

        attempt = 0
        while True:
            try:
                response = self._session.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    headers=combined_headers or None,
                    timeout=timeout,
                )
            except requests.RequestException as exc:  # type: ignore[attr-defined]
                if attempt < self._max_retries:
                    self._sleep_with_backoff(attempt)
                    attempt += 1
                    continue
                raise NetworkError(f"Network error: {exc}") from exc

            payload = _parse_response(response)
            if response.status_code >= 400:
                if _should_retry(response.status_code) and attempt < self._max_retries:
                    self._sleep_with_backoff(attempt)
                    attempt += 1
                    continue
                raise_for_status(response.status_code, payload)
            return payload

    def _sleep_with_backoff(self, attempt: int) -> None:
        delay = self._retry_backoff * (2**attempt)
        jitter = (
            random.uniform(0, self._retry_backoff / 2) if self._retry_backoff else 0
        )
        time.sleep(delay + jitter)

    def close(self) -> None:
        close = getattr(self._session, "close", None)
        if callable(close):
            close()


class AsyncHTTPTransport:
    """Async counterpart built on :mod:`aiohttp`. Supports retries."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_backoff: float = DEFAULT_RETRY_BACKOFF,
        session: Optional[Any] = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max(0, max_retries)
        self._retry_backoff = max(0.0, retry_backoff)
        self._session = session

    async def _ensure_session(self) -> Any:
        if aiohttp is None:
            raise RuntimeError(
                "The 'aiohttp' package is required for asynchronous HTTP transport"
            ) from _aiohttp_error
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=self._timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)  # type: ignore[attr-defined]
        return self._session

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Any = None,
        headers: Optional[Mapping[str, str]] = None,
        options: Optional[RequestOptions] = None,
    ) -> dict[str, Any]:
        opts = options or RequestOptions()
        timeout = opts.timeout if opts.timeout is not None else self._timeout
        base_url = opts.base_url or self._base_url
        url = _build_url(base_url, path)

        combined_headers: dict[str, str] = {}
        if headers:
            combined_headers.update(headers)
        if opts.headers:
            combined_headers.update(opts.headers)

        attempt = 0
        while True:
            session = await self._ensure_session()
            try:
                async with session.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    headers=combined_headers or None,
                    timeout=timeout,
                ) as response:
                    payload = await _parse_async_response(response)
                    if response.status >= 400:
                        if (
                            _should_retry(response.status)
                            and attempt < self._max_retries
                        ):
                            await self._sleep_with_backoff(attempt)
                            attempt += 1
                            continue
                        raise_for_status(response.status, payload)
                    return payload
            except _AIOHTTP_CLIENT_ERROR as exc:  # type: ignore[misc]
                if attempt < self._max_retries:
                    await self._sleep_with_backoff(attempt)
                    attempt += 1
                    continue
                raise NetworkError(f"Network error: {exc}") from exc

    async def close(self) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def _sleep_with_backoff(self, attempt: int) -> None:
        delay = self._retry_backoff * (2**attempt)
        jitter = (
            random.uniform(0, self._retry_backoff / 2) if self._retry_backoff else 0
        )
        await asyncio.sleep(delay + jitter)


__all__ = [
    "RequestOptions",
    "SyncHTTPTransport",
    "AsyncHTTPTransport",
]
