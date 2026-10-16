"""P5 router: Dijkstra vs A* on KFS graph. Owner: P5."""
from __future__ import annotations

from pathlib import Path

from achtung.core.base import RouterPlugin
from achtung.core.context import PluginContext
from achtung.core.models import RoutePath

GRAPH = Path(__file__).parent.parent.parent / "data" / "kfs_graph.json"


class Router(RouterPlugin):
    name = "router"

    def setup(self, ctx: PluginContext) -> None:
        """Load graph into adj list."""
        # TODO(P5): implement.
        raise NotImplementedError

    def run(self, ctx: PluginContext) -> RoutePath:
        """Demo route: user -> food."""
        # TODO(P5): implement.
        raise NotImplementedError

    def route(
        self, ctx: PluginContext, start: tuple[float, float], end: tuple[float, float], algo: str = "astar"
    ) -> RoutePath:
        """Dispatch to dijkstra or astar."""
        # TODO(P5): implement.
        raise NotImplementedError
