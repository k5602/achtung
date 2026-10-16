"""P1 collector: live APIs with mock fallback. Owner: P1."""
from __future__ import annotations

from pathlib import Path

from achtung.core.base import CollectorPlugin
from achtung.core.context import PluginContext
from achtung.core.models import DisasterReport

MOCK = Path(__file__).parent.parent.parent / "data" / "kfs_mock.json"

# TODO(P1): set ReliefWeb + GDACS URLs, keep timeout <= 5s.


class Collector(CollectorPlugin):
    name = "collector"

    def setup(self, ctx: PluginContext) -> None:
        """Load nothing. Must work offline."""
        # TODO(P1): implement.
        raise NotImplementedError

    def run(self, ctx: PluginContext) -> list[DisasterReport]:
        """Registry entry. Delegate to collect."""
        # TODO(P1): implement.
        raise NotImplementedError

    def collect(self, ctx: PluginContext) -> list[DisasterReport]:
        """Try live, fallback to MOCK. Fill ctx.store."""
        # TODO(P1): implement.
        raise NotImplementedError
