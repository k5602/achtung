#cspell:disable
"""P5 router: safe routing. Owner: P5.

Shortest path on data/kfs_graph.json (road nodes + km edges).
Implements Dijkstra (baseline) vs A* (haversine heuristic).
Takes ctx (shared context object passed to every plugin).
Reports km + expanded nodes for evaluator.
"""
from achtung.plugins.router.plugin import Router

__all__ = ["Router"]
