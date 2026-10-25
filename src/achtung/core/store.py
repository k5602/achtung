"""Shared in-memory store. Plugins talk via store, never directly."""
from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from achtung.core.models import DisasterReport, Resource


class InMemoryStore:
    """Lists for reports/resources. hours_ago -> observed_at on load."""

    def __init__(self) -> None:
        self.reports: list[DisasterReport] = []
        self.resources: list[Resource] = []
        self.now: datetime = datetime.now(UTC)

    def clear(self) -> None:
        """Reset for tests."""
        self.reports.clear()
        self.resources.clear()
        self.now = datetime.now(UTC)

    def load_mock(self, path: str | Path, now: datetime | None = None) -> None:
        """Load KFS fixture. now injectable for deterministic tests."""
        if now is not None:
            self.now = now
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        for r in raw.get("reports", []):
            self.reports.append(self._to_report(r))
        for r in raw.get("resources", []):
            self.resources.append(self._to_resource(r))

    def _to_report(self, r: dict[str, Any]) -> DisasterReport:
        """Convert hours_ago to absolute time."""
        return DisasterReport(
            id=r["id"],
            source=r["source"],
            text=r["text"],
            kind=r["kind"],
            lat=float(r["lat"]),
            lon=float(r["lon"]),
            hours_ago=float(r["hours_ago"]),
            observed_at=self.now - timedelta(hours=float(r["hours_ago"])),
            trust=float(r.get("trust", 0.5)),
            verified=bool(r.get("verified", False)),
        )

    def _to_resource(self, r: dict[str, Any]) -> Resource:
        """Plain mapping, no time math."""
        return Resource(
            id=r["id"],
            kind=r["kind"],
            name=r["name"],
            lat=float(r["lat"]),
            lon=float(r["lon"]),
            capacity=int(r.get("capacity", 0)),
            source=r.get("source", "unknown"),
            trust=float(r.get("trust", 0.5)),
            verified=bool(r.get("verified", False)),
        )
