"""Probe-related helpers for the ModelRed Python SDK.

The concrete implementation (fetching probe metadata, filtering, etc.) will be
added in the next steps of the refactor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..http import RequestOptions
from .base import SyncAPIResource, AsyncAPIResource


@dataclass(slots=True)
class Probe:
    """Data structure describing a single probe definition."""

    id: str
    key: str
    display_name: str
    description: str
    estimated_time: str
    tags: List[str]
    category: str
    tier: str
    severity: str
    is_active: bool
    version: str


def parse_probe(payload: Dict[str, Any]) -> Probe:
    """Convert a raw API payload into a ``Probe`` instance.

    The function normalises field names and ensures case-insensitive
    handling of category, severity, and tier values for robust filtering.
    """

    return Probe(
        id=payload["id"],
        key=payload["key"],
        display_name=payload.get("display_name", payload.get("displayName", "")),
        description=payload.get("description", ""),
        estimated_time=payload.get("estimated_time", ""),
        tags=list(payload.get("tags", [])),
        category=payload.get("category", "").lower(),  # Normalize to lowercase
        tier=payload.get("tier", "").lower(),  # Normalize to lowercase
        severity=payload.get("severity", "").lower(),  # Normalize to lowercase
        is_active=payload.get("isActive", True),
        version=payload.get("version", "1.0"),
    )


@dataclass(slots=True)
class ProbeIndex:
    """Collection of probes plus supporting metadata."""

    probes: List[Probe]
    probe_categories: Dict[str, Any]
    tier_definitions: Dict[str, Any]
    severity_levels: Dict[str, Any]
    user_tier: Optional[str] = None  # User's subscription tier from backend


def parse_probe_index(payload: Dict[str, Any]) -> ProbeIndex:
    data = payload.get("data", payload)
    meta = payload.get("meta", {})
    probes = [parse_probe(item) for item in data.get("probes", [])]
    return ProbeIndex(
        probes=probes,
        probe_categories=data.get("probe_categories", {}),
        tier_definitions=data.get("tier_definitions", {}),
        severity_levels=data.get("severity_levels", {}),
        user_tier=meta.get("user_tier"),  # Extract user tier from metadata
    )


class ProbesClient(SyncAPIResource):
    """Synchronous helper for `/probes` filters and listings."""

    _RESOURCE_PATH = "/probes"

    def list(
        self,
        *,
        category: Optional[str] = None,
        tier: Optional[str] = None,
        severity: Optional[str] = None,
        options: Optional[RequestOptions] = None,
    ) -> ProbeIndex:
        params: Dict[str, str] = {}
        if category:
            params["category"] = category
        if tier:
            params["tier"] = tier
        if severity:
            params["severity"] = severity
        params["pageSize"] = "200"
        payload = self._request(
            "GET", self._RESOURCE_PATH, params=params or None, options=options
        )
        return parse_probe_index(payload)


class AsyncProbesClient(AsyncAPIResource):
    """Async helper for `/probes` listings."""

    _RESOURCE_PATH = "/probes"

    async def list(
        self,
        *,
        category: Optional[str] = None,
        tier: Optional[str] = None,
        severity: Optional[str] = None,
        options: Optional[RequestOptions] = None,
    ) -> ProbeIndex:
        params: Dict[str, str] = {}
        if category:
            params["category"] = category
        if tier:
            params["tier"] = tier
        if severity:
            params["severity"] = severity
        # Request all probes (max 200 per API, but typically <250 total)
        params["pageSize"] = "200"
        payload = await self._request(
            "GET", self._RESOURCE_PATH, params=params or None, options=options
        )
        return parse_probe_index(payload)
