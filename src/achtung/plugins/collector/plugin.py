"""P1 collector: live APIs with mock fallback. Owner: P1."""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import requests

from achtung.core.base import CollectorPlugin
from achtung.core.context import PluginContext
from achtung.core.models import DisasterReport

MOCK = Path(__file__).parent.parent.parent / "data" / "kfs_mock.json"

# Live feed: NASA EONET (TODO arch target is ReliefWeb + GDACS).
EONET_URL = "https://eonet.gsfc.nasa.gov/api/v3/events"
EONET_PARAMS = {"limit": 50, "days": 7, "status": "open"}
TIMEOUT = 5


class Collector(CollectorPlugin):
    name = "collector"

    def setup(self, ctx: PluginContext) -> None:
        """Load nothing. Must work offline."""

    def run(self, ctx: PluginContext) -> list[DisasterReport]:
        """Registry entry. Delegate to collect."""
        return self.collect(ctx)

    def collect(self, ctx: PluginContext) -> list[DisasterReport]:
        """Try live, fallback to MOCK. Fill ctx.store."""
        ctx.store.clear()
        ctx.store.load_mock(MOCK)  # resources for matcher + offline reports
        if not ctx.config.get("offline"):
            live = self._fetch_live()
            if live:
                ctx.store.reports.clear()
                ctx.store.reports.extend(live)
        return ctx.store.reports

    def _fetch_live(self) -> list[DisasterReport]:
        """Recent EONET events as reports; empty list when the fetch fails."""
        try:
            resp = requests.get(EONET_URL, params=EONET_PARAMS, timeout=TIMEOUT)
            resp.raise_for_status()
            events = resp.json().get("events", [])
        except (requests.RequestException, ValueError):
            return []  # offline / bad status / bad JSON

        reports: list[DisasterReport] = []
        for event in events:
            try:
                report = self._from_eonet(event)
            except (KeyError, IndexError, TypeError, ValueError):
                continue  # schema drift: skip the event
            if report is not None:
                reports.append(report)
        return reports

    def _from_eonet(self, event: dict) -> DisasterReport | None:
        """Map one EONET event to a report; None if it has no geometry."""
        geometry = event.get("geometry") or []
        if not geometry:
            return None
        point = geometry[-1]  # newest point of the track
        observed_at = datetime.fromisoformat(point["date"])
        categories = event.get("categories") or []
        return DisasterReport(
            id=event["id"],
            source="NASA EONET",
            text=event["title"],
            kind=categories[0]["title"] if categories else "unknown",
            lat=float(point["coordinates"][1]),
            lon=float(point["coordinates"][0]),
            hours_ago=round((datetime.now(UTC) - observed_at).total_seconds() / 3600, 2),
            observed_at=observed_at,
            trust=0.5,
            verified=False,
        )
