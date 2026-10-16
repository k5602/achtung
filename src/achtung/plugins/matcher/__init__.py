"""P4 matcher: resource matching. Owner: P4.

Ranks resources (ctx.store.resources = aid points list)
for a UserQuery (user text + location + need) by weighted
score (dist + trust + capacity + freshness) using haversine.
Ships baseline() distance-sort for report comparison.
"""
from achtung.plugins.matcher.plugin import Matcher

__all__ = ["Matcher"]
