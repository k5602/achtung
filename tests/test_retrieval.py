"""Retrieval checks: the selected need ranks reports; nothing is dropped."""
from datetime import UTC, datetime
from pathlib import Path

from achtung.core.context import PluginContext
from achtung.core.models import DisasterReport, Need, UserQuery
from achtung.core.store import InMemoryStore
from achtung.main import NEEDS
from achtung.plugins.retrieval.plugin import Retrieval

DATA = Path(__file__).parent.parent / "src" / "achtung" / "data"
KFS = (31.0968, 30.9516)
NOW = datetime(2026, 10, 16, 12, 0, 0, tzinfo=UTC)


def make_ctx() -> tuple[PluginContext, Retrieval]:
    store = InMemoryStore()
    store.load_mock(DATA / "kfs_mock.json")
    ctx = PluginContext(store=store, config={})
    return ctx, Retrieval()


def q(need: Need = "all") -> UserQuery:
    return UserQuery(need=need, lat=KFS[0], lon=KFS[1])


def report(kind: str, trust: float = 0.9, rid: str = "t1") -> DisasterReport:
    return DisasterReport(
        id=rid, source="s", text="stub", kind=kind,
        lat=31.1, lon=30.95, hours_ago=1,
        observed_at=NOW, trust=trust, verified=True,
    )


def test_food_need_puts_food_aid_first():
    ctx, r = make_ctx()
    hits = r.search(ctx, q("food"))
    assert hits[0].id == "rep-crescent-01"


def test_medical_need_top_hit_is_clinic_report():
    ctx, r = make_ctx()
    assert r.search(ctx, q("medical"))[0].id == "rep-crescent-02"


def test_all_need_returns_everything_by_trust():
    ctx, r = make_ctx()
    hits = r.search(ctx, q("all"))
    assert len(hits) == len(ctx.store.reports)
    trusts = [h.trust for h in hits]
    assert trusts == sorted(trusts, reverse=True)


def test_every_need_never_drops_reports():
    ctx, r = make_ctx()
    for need in NEEDS:
        assert len(r.search(ctx, q(need))) == len(ctx.store.reports)


def test_kind_match_grouping():
    """Kind matches first, trust order inside, high-trust noise after."""
    ctx, r = make_ctx()
    ctx.store.reports.clear()
    noise = report("road_alert", trust=1.0, rid="n1")
    serving_low = report("food_aid", trust=0.5, rid="s1")
    serving_high = report("food_aid", trust=0.9, rid="s2")
    ctx.store.reports.extend([noise, serving_low, serving_high])
    hits = r.search(ctx, q("food"))
    assert [h.id for h in hits] == ["s2", "s1", "n1"]


def test_empty_store_returns_empty():
    ctx, r = make_ctx()
    ctx.store.reports.clear()
    for need in NEEDS:
        assert r.search(ctx, q(need)) == []


def test_run_uses_query_from_config():
    ctx, r = make_ctx()
    ctx.config["query"] = q("medical")
    assert r.run(ctx)[0].id == "rep-crescent-02"
