"""P4 matcher: distance-sort baseline vs weighted rank. Owner: P4."""
from __future__ import annotations

from achtung.core.base import MatcherPlugin
from achtung.core.context import PluginContext
from achtung.core.models import RankedResult, Resource, UserQuery

# TODO(P4): set weights W_DIST=0.4, W_TRUST=0.3, W_CAP=0.2, W_FRESH=0.1.


class Matcher(MatcherPlugin):
    name = "matcher"

    def setup(self, ctx: PluginContext) -> None:
        """Stateless."""
        # TODO(P4): implement.
        raise NotImplementedError

    def run(self, ctx: PluginContext) -> list[RankedResult]:
        """Rank store resources for query in config."""
        # TODO(P4): implement.
        raise NotImplementedError

    def rank(
        self, ctx: PluginContext, query: UserQuery, resources: list[Resource]
    ) -> list[RankedResult]:
        """Weighted score. Filter by need unless need == all."""
        # TODO(P4): implement.
        raise NotImplementedError

    def baseline(self, query: UserQuery, resources: list[Resource]) -> list[RankedResult]:
        """Pure distance sort. Baseline for evaluator."""
        # TODO(P4): implement.
        raise NotImplementedError
