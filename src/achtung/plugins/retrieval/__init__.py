"""P2 retrieval: information retrieval. Owner: P2.

Ranks ctx.store.reports (collected disaster posts) for
a UserQuery (user text + location + need).
Method: inverted index + TF-IDF (BM25 stretch goal),
AR-EN synonym map from data/synonyms_ar_en.json.
"""
from achtung.plugins.retrieval.plugin import Retrieval

__all__ = ["Retrieval"]
