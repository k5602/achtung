"""P6 evaluator: per-query timing + baseline/A* comparisons. Owner: yahia."""
from __future__ import annotations

import time

from achtung.core.base import EvaluatorPlugin
from achtung.core.context import PluginContext
from achtung.core.models import EvaluateResult, UserQuery
from achtung.core.registry import get

RUNS = 20


class Evaluator(EvaluatorPlugin):
    """One EvaluateResult (20-run means) per query."""

    name = "evaluator"

    def __init__(self) -> None:
        self.results: list[EvaluateResult] = []

    def setup(self, ctx: PluginContext) -> None:
        """Stateless. """

    def run(self, ctx: PluginContext) -> EvaluateResult:
        """Registry entry. Delegate to typed method."""
        return self.evaluate(ctx, ctx.config["query"])

    @property
    def count(self) -> int:
        """Queries evaluated so far."""
        return len(self.results)

    def reset(self) -> None:
        self.results.clear()

    def evaluate(self, ctx: PluginContext, query: UserQuery) -> EvaluateResult:
        """Time RUNS passes on the filled store + deterministic comparisons."""
        retrieval, verifier, matcher, router = (
            get(n) for n in ("retrieval", "verifier", "matcher", "router")
        )
        start = (query.lat, query.lon)

        # Route target: None when no aid point matches — NO default.
        target = matcher.rank(ctx, query, ctx.store.resources)
        end = (target[0].resource.lat, target[0].resource.lon) if target else None

        retrieve_s: list[float] = []
        verify_s: list[float] = []
        match_s: list[float] = []
        routing_s: list[float] = []
        total_s: list[float] = []
        hits: list = []
        for _ in range(RUNS):
            # init time .
            t_all = time.perf_counter()

            t = time.perf_counter()
            hits = retrieval.search(ctx, query)
            retrieve_s.append((time.perf_counter() - t) * 1000.0)

            t = time.perf_counter()
            verifier.verify(ctx, hits)
            verify_s.append((time.perf_counter() - t) * 1000.0)

            t = time.perf_counter()
            ranked = matcher.rank(ctx, query, ctx.store.resources)
            match_s.append((time.perf_counter() - t) * 1000.0)
            
            # if destination exists.
            if end is not None:
                t = time.perf_counter()
                router.route(ctx, start, end, algo="astar")
                routing_s.append((time.perf_counter() - t) * 1000.0)

            total_s.append((time.perf_counter() - t_all) * 1000.0)

        baseline = matcher.baseline(query, ctx.store.resources)
        baseline_ids = [r.resource.id for r in baseline]
        weighted_ids = [r.resource.id for r in ranked]
        baseline_top1 = baseline_ids[0] if baseline_ids else ""
        weighted_top1 = weighted_ids[0] if weighted_ids else ""
        swap = weighted_ids.index(baseline_top1) if baseline_top1 in weighted_ids else -1

        dijkstra_km: float | None = None
        astar_km: float | None = None
        dijkstra_expanded: int | None = None
        astar_expanded: int | None = None
        if end is not None:
            by_dijkstra = router.route(ctx, start, end, algo="dijkstra")
            by_astar = router.route(ctx, start, end, algo="astar")
            dijkstra_km = by_dijkstra.distance_km
            astar_km = by_astar.distance_km
            dijkstra_expanded = by_dijkstra.expanded
            astar_expanded = by_astar.expanded

        result = EvaluateResult(
            text=query.text,
            need=query.need,
            runs=RUNS,
            retrieval_ms=sum(retrieve_s) / RUNS,
            verify_ms=sum(verify_s) / RUNS,
            match_ms=sum(match_s) / RUNS,
            route_ms=(sum(routing_s) / len(routing_s)) if routing_s else None,
            total_ms=sum(total_s) / RUNS,
            total_min_ms=min(total_s),
            total_max_ms=max(total_s),
            hits=len(hits),
            baseline_top1=baseline_top1,
            weighted_top1=weighted_top1,
            top1_agree=baseline_top1 == weighted_top1 and bool(baseline_top1),
            swap=swap,
            dijkstra_km=dijkstra_km,
            astar_km=astar_km,
            dijkstra_expanded=dijkstra_expanded,
            astar_expanded=astar_expanded,
        )
        self.results.append(result)
        return result
