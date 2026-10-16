# cspell:disable

"""Router behavior: Dijkstra vs A* algorithms, setup and plugin run execution."""
from achtung.core.registry import get
from achtung.main import build_ctx
from achtung.plugins.router.algorithms import astar, dijkstra


def test_dijkstra_and_astar_correctness():
    sample_graph = {
        "A": {"B": 1, "C": 4},
        "B": {"A": 1, "C": 2, "D": 5},
        "C": {"A": 4, "B": 2, "D": 1},
        "D": {"B": 5, "C": 1},
    }
    path_d, dist_d, exp_d = dijkstra(sample_graph, "A", "D")
    path_a, dist_a, exp_a = astar(sample_graph, "A", "D")

    assert path_d == ["A", "B", "C", "D"]
    assert dist_d == 4
    assert path_a == ["A", "B", "C", "D"]
    assert dist_a == 4


def test_router_setup_and_execution():
    ctx = build_ctx()
    router = get("router")
    router.setup(ctx)

    assert router.adj is not None
    
    # Test route execution with lat/lon
    route_res = router.run(ctx)
    assert route_res is not None
    assert route_res.algo == "dijkstra"