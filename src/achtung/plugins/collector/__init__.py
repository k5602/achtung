"""P1 collector: data collection. Owner: P1.

Pulls reports from trusted APIs (ReliefWeb, GDACS),
falls back to data/kfs_mock.json offline.
Fills ctx.store (shared memory all plugins read/write).
First in pipeline.
"""
from achtung.plugins.collector.plugin import Collector

__all__ = ["Collector"]
