"""Core configuration values for the ModelRed Python SDK.

This module centralizes default endpoints, timeouts, and header constants so
other modules can import shared values without causing circular dependencies.
Detailed behaviour (retry policies, environment overrides, etc.) will be added
in later steps of the refactor.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Final

DEFAULT_BASE_URL: Final[str] = "https://app.modelred.ai/api"

# Environment variable names recognised by the SDK.
API_KEY_ENV_VAR: Final[str] = "MODELRED_API_KEY"
# SECURITY: base_url is only configurable via environment variable for dev/test purposes
# Users should NEVER be allowed to set this programmatically
BASE_URL_ENV_VAR: Final[str] = "MODELRED_BASE_URL"
TIMEOUT_ENV_VAR: Final[str] = "MODELRED_TIMEOUT"
MAX_RETRIES_ENV_VAR: Final[str] = "MODELRED_MAX_RETRIES"
RETRY_BACKOFF_ENV_VAR: Final[str] = "MODELRED_RETRY_BACKOFF"

# Default timeouts (in seconds) used by sync/async clients unless overridden by
# the caller.
DEFAULT_TIMEOUT: Final[float] = 30.0

# Retry configuration defaults. Backoff is exponential with jitter, starting at
# ``DEFAULT_RETRY_BACKOFF`` seconds.
DEFAULT_MAX_RETRIES: Final[int] = 3
DEFAULT_RETRY_BACKOFF: Final[float] = 0.5

# Header keys used throughout the SDK.
HEADER_AUTHORIZATION: Final[str] = "Authorization"
HEADER_ORGANIZATION_ID: Final[str] = "x-organization-id"
HEADER_API_KEY: Final[str] = "x-api-key"

USER_AGENT_TEMPLATE: Final[str] = "ModelRed-PythonSDK/{version}"


@dataclass(frozen=True, slots=True)
class SDKSettings:
    """Immutable container for runtime SDK configuration."""

    base_url: str = DEFAULT_BASE_URL
    timeout: float = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES
    retry_backoff: float = DEFAULT_RETRY_BACKOFF


def _sanitize_base_url(value: str) -> str:
    value = value.strip()
    if not value:
        return DEFAULT_BASE_URL
    # Prevent double slashes when joining paths.
    return value[:-1] if value.endswith("/") else value


def _safe_float(value: str | None, default: float) -> float:
    if value is None:
        return default
    try:
        parsed = float(value)
        return parsed if parsed > 0 else default
    except ValueError:
        return default


def _safe_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
        return parsed if parsed >= 0 else default
    except ValueError:
        return default


def load_settings(
    *,
    timeout: float | None = None,
    max_retries: int | None = None,
    retry_backoff: float | None = None,
) -> SDKSettings:
    """Create :class:`SDKSettings` using env fallbacks.

    SECURITY NOTE: base_url is ONLY configurable via MODELRED_BASE_URL environment variable.
    This prevents users from redirecting SDK traffic to malicious endpoints programmatically.
    """

    # SECURITY: Only read base_url from environment variable, never from parameters
    env_base = os.getenv(BASE_URL_ENV_VAR)
    resolved_base = env_base or DEFAULT_BASE_URL

    timeout_value = (
        timeout
        if timeout is not None
        else _safe_float(os.getenv(TIMEOUT_ENV_VAR), DEFAULT_TIMEOUT)
    )

    retries_value = (
        max_retries
        if max_retries is not None
        else _safe_int(os.getenv(MAX_RETRIES_ENV_VAR), DEFAULT_MAX_RETRIES)
    )

    backoff_value = (
        retry_backoff
        if retry_backoff is not None
        else _safe_float(os.getenv(RETRY_BACKOFF_ENV_VAR), DEFAULT_RETRY_BACKOFF)
    )

    return SDKSettings(
        base_url=_sanitize_base_url(resolved_base),
        timeout=timeout_value,
        max_retries=retries_value,
        retry_backoff=backoff_value,
    )


__all__ = [
    "API_KEY_ENV_VAR",
    "BASE_URL_ENV_VAR",
    "HEADER_API_KEY",
    "HEADER_AUTHORIZATION",
    "HEADER_ORGANIZATION_ID",
    "DEFAULT_BASE_URL",
    "DEFAULT_TIMEOUT",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_RETRY_BACKOFF",
    "USER_AGENT_TEMPLATE",
    "SDKSettings",
    "load_settings",
]
