#cspell:disable


"""P5 router: Dijkstra vs A* on KFS graph. Owner: P5."""
from __future__ import annotations
from pathlib import Path
from achtung.core.base import RouterPlugin
from achtung.core.context import PluginContext
from achtung.core.models import RoutePath

from .graph_loader import load_graph
from .algorithms import dijkstra, astar

GRAPH = Path(__file__).parent.parent.parent / "data" / "kfs_graph.json"


class Router(RouterPlugin):
    name = "router"

    def setup(self, ctx: PluginContext) -> None:

        """Load graph into adj list."""

        self.graph = load_graph()
        ctx.store["graph"] = self.graph



    def route(
        self, ctx: PluginContext, start: tuple[float, float], end: tuple[float, float], algo: str = "astar"
    ) -> RoutePath:
        
        """Dispatch to dijkstra or astar."""

        if not hasattr(self, "graph") or self.graph is None:
            self.graph = load_graph()

        if str(algo).lower()=="dijkstra":
            path , distance = dijkstra(self.graph , start , end)
        else:
            path , distance = astar(self.graph ,start , end)

        try:
            return RoutePath(path=path, distance=distance)

        except TypeError:
            return RoutePath(nodes=path , total_distance=distance)

        

    def run(self , ctx: PluginContext) -> RoutePath:

        """Demo route: user -> food."""

        start = ctx.store.get("user_location") or ctx.store.get("start")
        end = ctx.store.get("food_location") or ctx.store.get("target") or ctx.store.get("destination")

        if not start or not end:
            nodes = list(self.graph.keys()) if hasattr(self, "graph") and self.graph else []
            if len(nodes) >= 2:
                start = start or nodes[0]
                end = end or nodes[1]

        result_route = self.route(ctx, start=start, end=end, algo="astar")
        ctx.store["route"] = result_route
        return result_route