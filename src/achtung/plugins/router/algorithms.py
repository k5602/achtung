# cspell:disable
"""Dijkstra and A*. Edge weights are km."""
import heapq

from achtung.core.geo import haversine_km

from .graph_loader import Adjacency, NodeCoords


def dijkstra(graph: Adjacency, start: str, end: str) -> tuple[list[str], float, int]:
    """Shortest path; returns (path, km, nodes expanded)."""
    queue: list[tuple[float, str]] = [(0.0, start)]
    distances: dict[str, float] = {start: 0.0}
    came_from: dict[str, str] = {}
    expanded = 0

    while queue:
        current_distance, current_node = heapq.heappop(queue)
        if current_distance > distances.get(current_node, float("inf")):
            continue  # stale queue entry

        expanded += 1

        if current_node == end:
            break

        for neighbor, weight in graph.get(current_node, {}).items():
            distance = current_distance + weight
            if distance < distances.get(neighbor, float("inf")):
                distances[neighbor] = distance
                came_from[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    if end not in came_from and end != start:
        return [], float("inf"), expanded

    path = []
    curr = end
    while curr in came_from:
        path.append(curr)
        curr = came_from[curr]
    path.append(start)
    path.reverse()

    return path, distances.get(end, float("inf")), expanded


def heuristic_scale(graph: Adjacency, coords: NodeCoords) -> float:
    """Largest factor that keeps the straight-line heuristic consistent.

    Some mock edges are shorter than the straight-line gap between their
    endpoints, so a plain straight-line guess overestimates and A* loses
    optimality, so we scale by min(weight / straight) to restore the optimality.
    """
    ratios: list[float] = []
    for u, neighbors in graph.items():
        for v, weight in neighbors.items():
            if u < v and u in coords and v in coords and weight > 0:
                straight = haversine_km(*coords[u], *coords[v])
                if straight > 0:
                    ratios.append(weight / straight)
    return 0.999 * min(ratios) if ratios else 1.0


def astar(
    graph: Adjacency, start: str, end: str, coords: NodeCoords | None = None
) -> tuple[list[str], float, int]:
    """A* with a straight-line guess; returns (path, km, nodes expanded)."""
    scale = heuristic_scale(graph, coords) if coords else 1.0

    def h(node: str) -> float:
        if not coords or node not in coords or end not in coords:
            return 0.0
        return scale * haversine_km(*coords[node], *coords[end])

    queue: list[tuple[float, float, str]] = [(0.0, 0.0, start)]
    distances = {start: 0.0}
    came_from = {}
    expanded = 0

    while queue:
        _, current_distance, current_node = heapq.heappop(queue)
        if current_distance > distances.get(current_node, float("inf")):
            continue  # stale queue entry

        expanded += 1

        if current_node == end:
            break

        for neighbor, weight in graph.get(current_node, {}).items():
            distance = current_distance + weight
            if distance < distances.get(neighbor, float("inf")):
                distances[neighbor] = distance
                came_from[neighbor] = current_node
                heapq.heappush(queue, (distance + h(neighbor), distance, neighbor))

    if end not in came_from and end != start:
        return [], float("inf"), expanded

    path = []
    curr = end
    while curr in came_from:
        path.append(curr)
        curr = came_from[curr]
    path.append(start)
    path.reverse()

    return path, distances.get(end, float("inf")), expanded
