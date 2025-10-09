"""Custom exception hierarchy for the ModelRed Python SDK."""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional


class ModelRedError(Exception):
    """Base class for all SDK-specific exceptions."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response or {}


class AuthenticationError(ModelRedError):
    """Raised when the API rejects credentials."""


class AuthorizationError(ModelRedError):
    """Raised when a caller lacks permissions for the requested operation."""


class SubscriptionLimitError(ModelRedError):
    """Raised when an operation is blocked by the caller's subscription tier."""

    def __init__(
        self,
        message: str,
        tier: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(message, **kwargs)
        self.tier = tier


class ValidationError(ModelRedError):
    """Raised when payload validation fails."""


class NotFoundError(ModelRedError):
    """Raised when a requested resource is missing."""


class ConflictError(ModelRedError):
    """Raised when attempting to create a resource that already exists."""


class RateLimitError(ModelRedError):
    """Raised when the API throttles the request rate."""


class ServerError(ModelRedError):
    """Raised when the API returns a 5xx status code."""


class NetworkError(ModelRedError):
    """Raised when the underlying HTTP client encounters a connectivity issue."""


def raise_for_status(status: int, payload: Mapping[str, Any]) -> None:
    """Raise the appropriate SDK exception for a given HTTP status code."""

    message = (
        payload.get("error")
        or payload.get("message")
        or payload.get("detail")
        or f"API error {status}"
    )

    if status == 401:
        raise AuthenticationError(message, status, dict(payload))
    if status == 403:
        tier = payload.get("tier") if isinstance(payload, Mapping) else None
        if isinstance(message, str) and any(
            keyword in message.lower()
            for keyword in ("limit", "subscription", "tier", "upgrade")
        ):
            raise SubscriptionLimitError(
                message,
                tier=tier if isinstance(tier, str) else None,
                status_code=status,
                response=dict(payload),
            )
        raise AuthorizationError(message, status, dict(payload))
    if status == 404:
        raise NotFoundError(message, status, dict(payload))
    if status == 409:
        raise ConflictError(message, status, dict(payload))
    if status in (412, 422):
        raise ValidationError(message, status, dict(payload))
    if status == 429:
        raise RateLimitError(message, status, dict(payload))
    if status >= 500:
        raise ServerError(message, status, dict(payload))

    raise ModelRedError(message, status, dict(payload))


__all__ = [
    "ModelRedError",
    "AuthenticationError",
    "AuthorizationError",
    "SubscriptionLimitError",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "RateLimitError",
    "ServerError",
    "NetworkError",
    "raise_for_status",
]
