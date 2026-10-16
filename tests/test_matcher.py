"""Matcher behavior: filtering, ranking order, baseline vs weighted rank."""
from datetime import UTC, datetime
from pathlib import Path

from achtung.core.models import UserQuery
from achtung.core.registry import get
from achtung.main import build_ctx

MOCK = Path(__file__).resolve().parents[1] / "src" / "achtung" / "data" / "kfs_mock.json"
NOW = datetime(2026, 10, 16, 12, 0, 0, tzinfo=UTC)


def _ctx(need: str = "all"):
    ctx = build_ctx(need=need)
    ctx.store.load_mock(MOCK, now=NOW)
    return ctx


def test_run_returns_sorted_results():
    ctx = _ctx()
    results = get("matcher").run(ctx)
    assert results
    assert all(r.score >= 0 for r in results)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_filter_by_need():
    ctx = _ctx(need="food")
    results = get("matcher").run(ctx)
    assert results
    assert all(r.resource.kind == "food" for r in results)


def test_baseline_sorted_by_distance():
    ctx = _ctx()
    q: UserQuery = ctx.config["query"]
    results = get("matcher").baseline(q, ctx.store.resources)
    dists = [r.distance_km for r in results]
    assert dists == sorted(dists)
    # baseline score IS the distance (lower = closer)
    assert all(r.score == r.distance_km for r in results)


def test_nearest_resource_wins_baseline():
    ctx = _ctx()
    q: UserQuery = ctx.config["query"]
    results = get("matcher").baseline(q, ctx.store.resources)
    assert results[0].distance_km == min(r.distance_km for r in results)
