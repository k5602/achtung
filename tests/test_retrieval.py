"""retrieval checks: AR synonyms."""
from pathlib import Path

from achtung.core.context import PluginContext
from achtung.core.models import UserQuery
from achtung.core.store import InMemoryStore
from achtung.plugins.retrieval.plugin import Retrieval

DATA = Path(__file__).parent.parent / "src" / "achtung" / "data"
KFS = (31.0968, 30.9516)


def make_ctx() -> tuple[PluginContext, Retrieval]:
    store = InMemoryStore()
    store.load_mock(DATA / "kfs_mock.json")
    ctx = PluginContext(store=store, config={})
    r = Retrieval()
    r.setup(ctx)
    return ctx, r


def q(text: str, need: str = "all") -> UserQuery:
    return UserQuery(text=text, lat=KFS[0], lon=KFS[1], need=need)


def test_arabic_food_finds_food_aid():
    ctx, r = make_ctx()
    hits = r.search(ctx, q("اكل في كفر الشيخ"))
    assert hits and hits[0].kind in ("food_aid", "relief_center")
    assert any(h.id == "rep-crescent-01" for h in hits[:3])


def test_need_boost_and_medical_synonym():
    ctx, r = make_ctx()
    assert r.search(ctx, q("دواء", "medical"))[0].id == "rep-crescent-02"
    assert {h.kind for h in r.search(ctx, q("food", "food"))} <= {"food_aid"}


def test_empty_store_and_empty_query():
    ctx, r = make_ctx()
    ctx.store.reports.clear()
    assert r.search(ctx, q("food")) == []
