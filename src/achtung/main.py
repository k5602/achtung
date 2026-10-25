"""Achtung: KFS query."""
from __future__ import annotations

import argparse
import sys

import achtung.plugins  # noqa: F401  (registers all)
from achtung.core.context import PluginContext
from achtung.core.models import Need, UserQuery
from achtung.core.registry import get
from achtung.core.store import InMemoryStore

# KFS University anchor (0.8 / 1.2 / 1.5 km).
KFS_LAT, KFS_LON = 31.0968, 30.9516

NEEDS: tuple[Need, ...] = ("food", "water", "shelter", "medical", "all")


def build_ctx(need: str = "all") -> PluginContext:
    """Fresh store + KFS query for the need."""
    if need not in NEEDS:
        raise ValueError(f"unknown need {need!r}; expected one of {NEEDS}")
    store = InMemoryStore()
    return PluginContext(
        store=store,
        config={"offline": True, "query": UserQuery(need=need, lat=KFS_LAT, lon=KFS_LON)},
    )

# TODO add a --offline flag to avoid network calls (for demo purposes, we can use a local store with canned data).
# TODO add a --debug flag to show more verbose logs (for demo purposes, we can use a local store with canned data).
def main() -> None:
    """Open the TUI on a terminal; --cli (or a pipe) prints the plain demo."""
    ap = argparse.ArgumentParser(description="Achtung SafeReach demo (KFS)")
    ap.add_argument("--need", default="all", choices=NEEDS, help="aid category to look up")
    ap.add_argument("--cli", action="store_true", help="plain output instead of the TUI")
    args = ap.parse_args()
    if not args.cli and sys.stdout.isatty():
        from achtung.tui import AchtungApp

        AchtungApp(build_ctx(args.need)).run()
        return
    ctx = build_ctx(args.need)
    q: UserQuery = ctx.config["query"]
    print(f"Need: {q.need}  (user: KFS University, {KFS_LAT}, {KFS_LON})\n")
    for name in ("collector", "retrieval", "verifier", "matcher", "router"):
        try:
            get(name).run(ctx)
            print(f"[{name}] ok")
        except NotImplementedError:
            print(f"[{name}] TODO(owner): not implemented")

if __name__ == "__main__":
    main()
