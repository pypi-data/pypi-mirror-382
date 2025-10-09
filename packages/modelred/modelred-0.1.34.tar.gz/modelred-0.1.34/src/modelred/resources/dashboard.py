"""Dashboard aggregate helpers for the ModelRed Python SDK."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(slots=True)
class DashboardSummary:
    """Placeholder structure for dashboard metrics."""

    raw: Dict[str, Any]
