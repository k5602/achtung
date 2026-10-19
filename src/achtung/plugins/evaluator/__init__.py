"""P6 evaluator: live query metrics. Owner: yahia.

Times every query the TUI runs (search/verify/rank/route ms), 
run the query N times and took the mean of it, and compares distance baseline vs
weighted top-1 plus Dijkstra vs A* (km + expanded). Shown in the TUI .
"""
from achtung.plugins.evaluator.plugin import Evaluator

__all__ = ["Evaluator"]
