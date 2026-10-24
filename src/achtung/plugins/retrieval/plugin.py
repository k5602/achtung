"""P2 retrieval: rank store reports for the selected need. Owner: P2."""
from __future__ import annotations

from achtung.core.base import RetrievalPlugin
from achtung.core.context import PluginContext
from achtung.core.models import DisasterReport, UserQuery


class Retrieval(RetrievalPlugin):
    name = "retrieval"

    def run(self, ctx: PluginContext) -> list[DisasterReport]:
        """Registry entry: search with the query in config."""
        return self.search(ctx, ctx.config["query"])

    def search(self, ctx: PluginContext, query: UserQuery) -> list[DisasterReport]:
        """Reports serving the need first, trust order inside. Never drops."""
        reports = sorted(ctx.store.reports, key=lambda r: -r.trust)
        if query.need != "all":
            # Stable sort: trust order survives inside each group.
            reports.sort(key=lambda r: not r.kind.startswith(query.need))
        return reports
