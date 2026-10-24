# cspell:disable
"""Router behavior: Dijkstra vs A* algorithms, graph loading, and plugin execution."""

import pytest

from achtung.core.registry import get
from achtung.main import build_ctx
from achtung.plugins.router.algorithms import astar, dijkstra, heuristic_scale


def test_dijkstra_and_astar_correctness():
    sample_graph = {
        "A": {"B": 1, "C": 4},
        "B": {"A": 1, "C": 2, "D": 5},
        "C": {"A": 4, "B": 2, "D": 1},
        "D": {"B": 5, "C": 1},
    }
    coords = {
        "A": (31.0968, 30.9516),
        "B": (31.0975, 30.9516),
        "C": (31.0982, 30.9516),
        "D": (31.0990, 30.9516),
    }
    path_d, dist_d, exp_d = dijkstra(sample_graph, "A", "D")
    path_a, dist_a, exp_a = astar(sample_graph, "A", "D", coords)

    assert heuristic_scale(sample_graph, coords) > 1
    assert path_d == path_a == ["A", "B", "C", "D"]
    assert dist_d == dist_a == 4
    assert exp_a <= exp_d


def test_astar_matches_dijkstra_on_every_pair():
    ctx = build_ctx()
    router = get("router")

    for start in router.adj:
        for end in router.adj:
            by_dijkstra = router.route(ctx, start, end, algo="dijkstra")
            by_astar = router.route(ctx, start, end, algo="astar")
            assert by_astar.distance_km == pytest.approx(by_dijkstra.distance_km)


def test_route_validation_and_snapping():
    ctx = build_ctx()
    router = get("router")

    snapped = router.route(ctx, (31.0968, 30.9516), (31.104, 30.9516))
    assert snapped.nodes[0] == "user"
    assert snapped.nodes[-1] == "food"

    with pytest.raises(ValueError):
        router.route(ctx, "user", "food", algo="dijkstr")

    with pytest.raises(ValueError):
        router.route(ctx, "user", "nosuch")


def test_router_graph_load_and_execution():
    ctx = build_ctx()
    router = get("router")

    assert len(router.adj) > 0

    route_res = router.run(ctx)
    assert route_res is not None
    assert len(route_res.nodes) > 0
    assert route_res.distance_km > 0.0
