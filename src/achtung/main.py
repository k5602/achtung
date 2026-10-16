"""Achtung demo: KFS query skeleton (plugins are stubs for now)."""
from __future__ import annotations

import argparse

import achtung.plugins  # noqa: F401  (registers all)
from achtung.core.context import PluginContext
from achtung.core.models import UserQuery
from achtung.core.registry import get
from achtung.core.store import InMemoryStore

# KFS University anchor (0.8 / 1.2 / 1.5 km).
KFS_LAT, KFS_LON = 31.0968, 30.9516


def build_ctx(need: str = "all", text: str = "اكل في كفر الشيخ") -> PluginContext:
    """Fresh store + default KFS query. setup_all tolerates stubs."""
    store = InMemoryStore()
    ctx = PluginContext(
        store=store,
        config={"offline": True, "query": UserQuery(text=text, lat=KFS_LAT, lon=KFS_LON, need=need)},
    )
    for name in ("collector", "retrieval", "verifier", "matcher", "router"):
        try:
            get(name).setup(ctx)
        except NotImplementedError:
            ctx.log(f"[{name}] TODO: setup not implemented")
    return ctx

# TODO(P1-P5): add a render() to show trusted/unverified/resources/route once plugins land.
# TODO add a --offline flag to avoid network calls (for demo purposes, we can use a local store with canned data).
# TODO add a --debug flag to show more verbose logs (for demo purposes, we can use a local store with canned data).
# TODO add a COOL TUI to show the query and the results
def main() -> None:
    """Try pipeline, report TODO status per plugin."""
    ap = argparse.ArgumentParser(description="Achtung SafeReach demo (KFS)")
    ap.add_argument("--need", default="all", help="food|shelter|medical|water|all")
    ap.add_argument("--text", default="اكل في كفر الشيخ", help="query text")
    args = ap.parse_args()
    ctx = build_ctx(args.need, args.text)
    q: UserQuery = ctx.config["query"]
    print(f'Query: "{q.text}"  (user: KFS University, {KFS_LAT}, {KFS_LON})\n')
    for name in ("collector", "retrieval", "verifier", "matcher", "router"):
        try:
            get(name).run(ctx)
            print(f"[{name}] ok")
        except NotImplementedError:
            print(f"[{name}] TODO(owner): not implemented")
    # TODO(P1-P5): render trusted/unverified/resources/route once plugins land.


if __name__ == "__main__":
    main()
