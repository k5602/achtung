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
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class Router(RouterPlugin):
    name = "router"

    def __init__(self):
        self.adj = {}
        self.coords = {}

    def setup(self, ctx: PluginContext) -> None:
        """Load graph data onto instance attributes."""
        self.adj, self.coords = load_graph()

    def _nearest_node(self, lat: float, lon: float) -> str:
        if not self.coords:
            nodes = list(self.adj.keys())
            return nodes[0] if nodes else ""
        return min(
            self.coords.keys(),
            key=lambda n: haversine_km(lat, lon, self.coords[n][0], self.coords[n][1])
        )

    def route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        algo: str = "dijkstra"
    ) -> RoutePath:
        start_node = self._nearest_node(start_lat, start_lon)
        end_node = self._nearest_node(end_lat, end_lon)

        if algo == "astar":
            path, dist, expanded = astar(self.adj, start_node, end_node, self.coords)
        else:
            path, dist, expanded = dijkstra(self.adj, start_node, end_node)

        return RoutePath(
            nodes=tuple(path),
            distance_km=float(dist if dist != float("inf") else 0.0),
            algo=algo,
            expanded=expanded
        )

    def run(self, ctx: PluginContext) -> RoutePath:
        query = ctx.config["query"]
        start_lat, start_lon = query.lat, query.lon
        
        # Default destination if needed (e.g. nearest node or query destination)
        end_lat, end_lon = start_lat, start_lon
        if self.coords:
            first_node = next(iter(self.coords))
            end_lat, end_lon = self.coords[first_node]

        return self.route(start_lat, start_lon, end_lat, end_lon, algo="dijkstra")