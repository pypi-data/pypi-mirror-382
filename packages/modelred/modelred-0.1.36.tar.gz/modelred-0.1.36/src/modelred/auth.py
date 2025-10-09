"""Authentication helpers for the ModelRed Python SDK.

Concrete header construction and API-key validation logic will live here. For
now, the module only exposes lightweight utilities that make it possible to
incrementally migrate existing client code during the refactor.
"""

from __future__ import annotations

import os
from typing import Optional

from .config import (
    API_KEY_ENV_VAR,
    HEADER_AUTHORIZATION,
    HEADER_ORGANIZATION_ID,
)
from .exceptions import ValidationError


def _normalise(api_key: str) -> str:
    return api_key.strip()


def is_valid_api_key(api_key: Optional[str]) -> bool:
    """Return ``True`` if the provided key looks like a ModelRed API key."""

    if not api_key:
        return False
    key = _normalise(api_key)
    return key.startswith("mr_") and len(key) >= 12


def validate_api_key(api_key: Optional[str]) -> str:
    """Validate and return a normalised API key.

    Raises :class:`ValidationError` if the key is missing or malformed.
    """

    if not api_key:
        raise ValidationError(
            "Valid API key is required (set MODELRED_API_KEY or pass api_key)."
        )
    key = _normalise(api_key)
    if not key.startswith("mr_"):
        raise ValidationError("ModelRed API keys must start with 'mr_'.")
    if len(key) < 12:
        raise ValidationError("ModelRed API keys appear to be malformed.")
    return key


def redact_api_key(api_key: Optional[str]) -> str:
    """Return a redacted form of the API key for logging purposes."""

    if not api_key:
        return "<missing>"
    key = _normalise(api_key)
    if len(key) <= 8:
        return "********"
    return f"{key[:4]}…{key[-4:]}"


def resolve_api_key(explicit: Optional[str] = None) -> str:
    """Return a usable API key from explicit argument or environment."""

    candidate = explicit or os.getenv(API_KEY_ENV_VAR)
    return validate_api_key(candidate)


def build_auth_headers(
    api_key: str,
    *,
    organization_id: Optional[str] = None,
) -> dict[str, str]:
    """Construct the headers required for authenticated requests."""

    key = validate_api_key(api_key)
    headers = {HEADER_AUTHORIZATION: f"Bearer {key}"}
    if organization_id:
        headers[HEADER_ORGANIZATION_ID] = organization_id
    return headers


__all__ = [
    "is_valid_api_key",
    "validate_api_key",
    "redact_api_key",
    "resolve_api_key",
    "build_auth_headers",
]
