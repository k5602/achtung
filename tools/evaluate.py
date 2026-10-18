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


class Evaluator:
    """Runs queries, keeps every result, exposes running means (TUI-injectable)."""

    def __init__(self) -> None:
        self.results: list[EvaluateResult] = []

    @property
    def count(self) -> int:
        """Number of queries evaluated so far (n of the running mean)."""
        return len(self.results)

    def evaluate(self, text: str, need: str = "all") -> EvaluateResult:
        """One query = one sample; appended to the running history."""
        result = evaluate_query(text, need)
        self.results.append(result)
        return result

    def mean(self, field: str) -> float:
        """Running mean sum/n for a timing field (n = queries so far)."""
        if not self.results:
            return 0.0
        return sum(getattr(r, field) for r in self.results) / len(self.results)

    def means(self) -> dict[str, float]:
        """Running means for all timing fields: n=1 -> t1, n=2 -> (t1+t2)/2."""
        return {f: self.mean(f) for f in MEAN_FIELDS}

    def reset(self) -> None:
        self.results.clear()


def format_report(results: list[EvaluateResult], means: dict[str, float]) -> str:
    """Three tables: timing , ranking swap, Dijkstra vs A*."""
    lines: list[str] = []

    lines.append("== Timing: one sample per query (ms) ==")
    lines.append(
        f"{'query':<28} {'need':<8} {'hits':>4} {'retrieval':>10} {'verify':>8} "
        f"{'match':>8} {'route':>8} {'total':>8}"
    )
    for r in results:
        lines.append(
            f"{r.text:<28.28} {r.need:<8} {r.hits:>4} {r.retrieval_ms:>10.3f} "
            f"{r.verify_ms:>8.3f} {r.match_ms:>8.3f} {r.route_ms:>8.3f} {r.total_ms:>8.3f}"
        )
    if results:
        n = len(results)
        lines.append(
            f"{'RUNNING MEAN':<28.28} {'':<8} {'':>4} {means['retrieval_ms']:>10.3f} "
            f"{means['verify_ms']:>8.3f} {means['match_ms']:>8.3f} "
            f"{means['route_ms']:>8.3f} {means['total_ms']:>8.3f}  (n={n})"
        )

    lines.append("")
    lines.append("== Ranking: distance baseline vs weighted ==")
    lines.append(
        f"{'query':<28} {'need':<8} {'baseline top1':<22} {'weighted top1':<22} "
        f"{'agree':>5} {'swap':>4}"
    )
    for r in results:
        lines.append(
            f"{r.text:<28.28} {r.need:<8} {r.baseline_top1:<22} {r.weighted_top1:<22} "
            f"{r.top1_agree!s:>5} {r.swap:>4}"
        )

    lines.append("")
    lines.append("== Routing: Dijkstra vs A* ==")
    lines.append(
        f"{'query':<28} {'need':<8} {'dijkstra km':>11} {'astar km':>9} "
        f"{'d_exp':>5} {'a_exp':>5} {'saved':>7}"
    )
    for r in results:
        saved = 100.0 * (1.0 - r.astar_expanded / r.dijkstra_expanded) if r.dijkstra_expanded else 0.0
        lines.append(
            f"{r.text:<28.28} {r.need:<8} {r.dijkstra_km:>11.3f} {r.astar_km:>9.3f} "
            f"{r.dijkstra_expanded:>5} {r.astar_expanded:>5} {saved:>6.1f}%"
        )
    return "\n".join(lines)


def main() -> None:
    """Evaluate the static project queries and print the report."""
    evaluator = Evaluator()
    results = [evaluator.evaluate(text, need) for text, need in QUERIES]
    print(format_report(results, evaluator.means()))


if __name__ == "__main__":
    main()
