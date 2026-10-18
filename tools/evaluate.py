"""Evaluator: IR + ranking + routing benchmarks for report."""
from __future__ import annotations

import time

from achtung.core.models import EvaluateResult, UserQuery
from achtung.core.registry import get
from achtung.main import KFS_LAT, KFS_LON, build_ctx

QUERIES: list[tuple[str, str]] = [
    ("اكل في كفر الشيخ", "all"),
    ("food", "all"),
    ("food", "food"),
    ("دواء", "medical"),
    ("ملجأ", "shelter"),
    ("مياه", "water"),
]

MEAN_FIELDS = ("retrieval_ms", "verify_ms", "match_ms", "route_ms", "total_ms")


def _quiet(_msg: str) -> None:
    """we didn't need spam prints in STDIO """


def evaluate_query(text: str, need: str = "all") -> EvaluateResult:
    """Time ONE real pipeline run + deterministic baseline/A* comparisons."""
    ctx = build_ctx(need=need, text=text)
    ctx.log = _quiet
    query: UserQuery = ctx.config["query"]
    retrieval, verifier, matcher, router = (
        get(n) for n in ("retrieval", "verifier", "matcher", "router")
    )

    t_all = time.perf_counter()
    get("collector").run(ctx)

    t = time.perf_counter()
    hits = retrieval.search(ctx, query)
    retrieval_ms = (time.perf_counter() - t) * 1000.0

    t = time.perf_counter()
    verifier.verify(ctx, hits)
    verify_ms = (time.perf_counter() - t) * 1000.0

    t = time.perf_counter()
    ranked = matcher.rank(ctx, query, ctx.store.resources)
    match_ms = (time.perf_counter() - t) * 1000.0

    start = (KFS_LAT, KFS_LON)
    end = (ranked[0].resource.lat, ranked[0].resource.lon) if ranked else "food"
    t = time.perf_counter()
    router.route(ctx, start, end, algo="astar")
    route_ms = (time.perf_counter() - t) * 1000.0

    total_ms = (time.perf_counter() - t_all) * 1000.0

    # Ranking: distance baseline vs weighted ( top-1 ).
    baseline = matcher.baseline(query, ctx.store.resources)
    baseline_ids = [r.resource.id for r in baseline]
    weighted_ids = [r.resource.id for r in ranked]
    baseline_top1 = baseline_ids[0] if baseline_ids else ""
    weighted_top1 = weighted_ids[0] if weighted_ids else ""
    swap = weighted_ids.index(baseline_top1) if baseline_top1 in weighted_ids else -1

    # Routing: dijkstra vs astar (km + expanded), with same Final distination.
    by_dijkstra = router.route(ctx, start, end, algo="dijkstra")
    by_astar = router.route(ctx, start, end, algo="astar")

    return EvaluateResult(
        text=text,
        need=need,
        retrieval_ms=retrieval_ms,
        verify_ms=verify_ms,
        match_ms=match_ms,
        route_ms=route_ms,
        total_ms=total_ms,
        hits=len(hits),
        baseline_top1=baseline_top1,
        weighted_top1=weighted_top1,
        top1_agree=baseline_top1 == weighted_top1 and bool(baseline_top1),
        swap=swap,
        dijkstra_km=by_dijkstra.distance_km,
        astar_km=by_astar.distance_km,
        dijkstra_expanded=by_dijkstra.expanded,
        astar_expanded=by_astar.expanded,
    )




def main() -> None:
    """Print precision@k, ranking swap, Dijkstra vs A* table."""
    # TODO(owner): time retrieval.search, print ms.
    # TODO(owner): compare matcher.baseline vs matcher.rank top-1.
    # TODO(owner): compare router dijkstra vs astar (km + expanded).
    raise NotImplementedError


if __name__ == "__main__":
    main()
