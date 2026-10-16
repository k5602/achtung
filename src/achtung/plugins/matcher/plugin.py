"""P4 matcher: distance-sort baseline vs weighted rank. Owner: P4."""
from __future__ import annotations

from achtung.core.base import MatcherPlugin
from achtung.core.context import PluginContext
from achtung.core.geo import haversine_km
from achtung.core.models import RankedResult, Resource, UserQuery

# TODO(P4): set weights W_DIST=0.4, W_TRUST=0.3, W_CAP=0.2, W_FRESH=0.1. (Done) .


class Matcher(MatcherPlugin):
    name = "matcher"

    W_DIST = 0.4
    W_TRUST = 0.3
    W_CAP = 0.2
    W_FRESH = 0.1

    def setup(self, ctx: PluginContext) -> None:
        """Stateless."""
        # TODO(P4): implement(Done No need to Setup).
        return

    def run(self, ctx: PluginContext) -> list[RankedResult]:
        """Rank store resources for query in config."""
        query: UserQuery = ctx.config["query"]
        return self.rank(ctx, query, ctx.store.resources)

    def rank(
        self, ctx: PluginContext, query: UserQuery, resources: list[Resource]
    ) -> list[RankedResult]:
        """Weighted score. Filter by need unless need == all."""
        if query.need != "all":
            resources = [r for r in resources if r.kind == query.need]

        max_cap = max((r.capacity for r in resources), default=0)
        results: list[RankedResult] = []
        for r in resources:
            dist = haversine_km(query.lat, query.lon, r.lat, r.lon)
            s_dist = 1.0 / (1.0 + dist)
            s_trust = r.trust
            s_cap = (r.capacity / max_cap) if max_cap > 0 else 0.0
            s_fresh = self._freshness(ctx, r)
            score = (
                self.W_DIST * s_dist
                + self.W_TRUST * s_trust
                + self.W_CAP * s_cap
                + self.W_FRESH * s_fresh
            )
            results.append(
                RankedResult(resource=r, score=score, distance_km=dist, verified=r.verified)
            )
        results.sort(key=lambda x: x.score, reverse=True)
        return results

    def baseline(self, query: UserQuery, resources: list[Resource]) -> list[RankedResult]:
        """Pure distance sort. Baseline for evaluator."""
        if query.need != "all":
            resources = [r for r in resources if r.kind == query.need]
        results = [
            RankedResult(
                resource=r,
                score=haversine_km(query.lat, query.lon, r.lat, r.lon),
                distance_km=haversine_km(query.lat, query.lon, r.lat, r.lon),
                verified=r.verified,
            )
            for r in resources
        ]
        results.sort(key=lambda x: x.distance_km)
        return results

    @staticmethod
    def _freshness(ctx: PluginContext, resource: Resource) -> float:
        """Resources carry no timestamp: proxy with the newest nearby report.

        Nearest report within 5 km gives its age in hours; score = 1/(1+hours).
        Neutral 1.0 when no reports are available (offline / empty store).
        """
        best: float | None = None
        for rep in ctx.store.reports:
            d = haversine_km(resource.lat, resource.lon, rep.lat, rep.lon)
            if d > 5.0:
                continue
            if best is None or rep.hours_ago < best:
                best = rep.hours_ago
        if best is None:
            return 1.0
        return 1.0 / (1.0 + best)
