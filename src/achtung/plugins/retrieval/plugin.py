"""P2 retrieval: inverted index + TF-IDF. Owner: P2."""
from __future__ import annotations

from achtung.core.base import RetrievalPlugin
from achtung.core.context import PluginContext
from achtung.core.models import DisasterReport, UserQuery


class Retrieval(RetrievalPlugin):
    name = "retrieval"

    def setup(self, ctx: PluginContext) -> None:
        """Load synonyms, build empty index."""
        # TODO(P2): implement.
        raise NotImplementedError

    def run(self, ctx: PluginContext) -> list[DisasterReport]:
        """Default query from ctx.config for registry.run_all."""
        # TODO(P2): implement.
        raise NotImplementedError

    def normalize(self, text: str) -> list[str]:
        """Lowercase + AR-EN keyword map."""
        # TODO(P2): implement.
        raise NotImplementedError

    def search(self, ctx: PluginContext, query: UserQuery) -> list[DisasterReport]:
        """TF-IDF rank over ctx.store.reports."""
        # TODO(P2): implement (BM25 stretch goal).
        raise NotImplementedError
