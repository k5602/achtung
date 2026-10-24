"""P2 retrieval: information retrieval. Owner: P2.

Ranks ctx.store.reports (collected disaster posts) for
a UserQuery (user location + need).
Method: reports whose kind matches the need come first,
trust orders within; nothing is dropped.
"""
from achtung.plugins.retrieval.plugin import Retrieval

__all__ = ["Retrieval"]
