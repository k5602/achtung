"""Load the mock road graph (nodes with lat/lon + km edges from kfs_graph.json)."""
import json
from pathlib import Path
from typing import Any

Adjacency = dict[str, dict[str, float]]
NodeCoords = dict[str, tuple[float, float]]


def load_graph() -> tuple[Adjacency, NodeCoords]:
    """Return (adjacency, coordinates); empty dicts if the file is missing."""
    path = Path(__file__).resolve().parents[2] / "data" / "kfs_graph.json"
    if not path.exists():
        return {}, {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes = data.get("nodes", {})
    if isinstance(nodes, list):
        nodes_dict: dict[str, Any] = {n: {} for n in nodes}
    else:
        nodes_dict = nodes

    adj: Adjacency = {n: {} for n in nodes_dict}
    coords: NodeCoords = {}

    for n, info in nodes_dict.items():
        if isinstance(info, dict) and "lat" in info and "lon" in info:
            coords[n] = (info["lat"], info["lon"])
        elif isinstance(info, (list, tuple)) and len(info) >= 2:
            coords[n] = (info[0], info[1])

    for edge in data.get("edges", []):
        if len(edge) >= 3:
            u, v, w = edge[0], edge[1], edge[2]
            if u in adj and v in adj:
                weight = float(w)
                adj[u][v] = weight
                adj[v][u] = weight

    return adj, coords
