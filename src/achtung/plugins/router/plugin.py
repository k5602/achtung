# cspell:disable
import math
from achtung.core.base import RouterPlugin
from achtung.core.context import PluginContext
from achtung.core.models import RoutePath
from .algorithms import astar, dijkstra
from .graph_loader import load_graph


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class Router(RouterPlugin):
    name = "router"

    def __init__(self):
        self.adj = {}
        self.coords = {}

    def setup(self, ctx: PluginContext) -> None:
        """Load graph data onto instance attributes."""
        self.adj, self.coords = load_graph()

    def _nearest_node(self, target) -> str:
        if isinstance(target, str):
            return target
        if isinstance(target, (tuple, list)) and len(target) >= 2:
            lat, lon = float(target[0]), float(target[1])
            if not self.coords:
                nodes = list(self.adj.keys())
                return nodes[0] if nodes else ""
            return min(
                self.coords.keys(),
                key=lambda n: haversine_km(
                    lat, lon, self.coords[n][0], self.coords[n][1]
                ),
            )
        return str(target)

    def route(
        self,
        ctx: PluginContext,
        start: tuple[float, float] | str,
        end: tuple[float, float] | str,
        algo: str = "astar",
    ) -> RoutePath:
        start_node = self._nearest_node(start)
        end_node = self._nearest_node(end)

        if algo == "dijkstra":
            path, dist, expanded = dijkstra(self.adj, start_node, end_node)
        else:
            path, dist, expanded = astar(
                self.adj, start_node, end_node, self.coords
            )

        return RoutePath(
            nodes=tuple(path),
            distance_km=float(dist if dist != float("inf") else 0.0),
            algo=algo,
            expanded=expanded,
        )

    def run(self, ctx: PluginContext) -> RoutePath:
        query = ctx.config.get("query")
        if query and hasattr(query, "lat") and hasattr(query, "lon"):
            start_pos = (query.lat, query.lon)
        elif "user" in self.coords:
            start_pos = self.coords["user"]
        else:
            start_pos = "user"

        if "food" in self.coords:
            end_pos = self.coords["food"]
        else:
            end_pos = "food"

        return self.route(ctx, start=start_pos, end=end_pos, algo="astar")