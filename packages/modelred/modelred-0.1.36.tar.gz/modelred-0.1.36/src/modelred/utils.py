"""General-purpose helpers for the ModelRed Python SDK."""

from __future__ import annotations

from datetime import datetime
from typing import Optional


def parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse an ISO-8601 timestamp into a ``datetime`` instance.

    The implementation mirrors the current behaviour in ``modelred.__init__``
    and provides a single place to enhance parsing (e.g. strict validation or
    fallback strategies) in later steps.
    """

    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None
