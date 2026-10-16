import json
from pathlib import Path


def load_graph():
    """Returns (adj, coords) from kfs_graph.json"""
    path = Path(__file__).resolve().parents[2] / "data" / "kfs_graph.json"
    if not path.exists():
        return {}, {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Parsing adj and coords
    adj = data.get("adj", data.get("graph", {}))
    coords = {}
    for node, info in data.get("nodes", {}).items():
        if isinstance(info, dict) and "lat" in info and "lon" in info:
            coords[node] = (info["lat"], info["lon"])
        elif isinstance(info, (list, tuple)) and len(info) >= 2:
            coords[node] = (info[0], info[1])

    return adj, coords