"""Plugin ABCs. Implement one per member, no cross-plugin imports PLLEEEAAAASE."""
from __future__ import annotations

from abc import ABC, abstractmethod

from achtung.core.context import PluginContext
from achtung.core.models import DisasterReport, RankedResult, Resource, RoutePath, UserQuery


class BasePlugin(ABC):
    name: str = "base"
    version: str = "0.1.0"

    @abstractmethod
    def setup(self, ctx: PluginContext) -> None:
        """Load files / build indexes. Must work offline."""

    @abstractmethod
    def run(self, ctx: PluginContext) -> object:
        """Default entry for registry.run_all. Delegate to typed method."""

    def health(self) -> bool:
        """Quick self-check for tests."""
        return True


class CollectorPlugin(BasePlugin):
    @abstractmethod
    def collect(self, ctx: PluginContext) -> list[DisasterReport]:
        """Fetch reports; fallback to mock on network failure."""


class RetrievalPlugin(BasePlugin):
    @abstractmethod
    def search(self, ctx: PluginContext, query: UserQuery) -> list[DisasterReport]:
        """TF-IDF/BM25 over store reports."""


class VerifierPlugin(BasePlugin):
    @abstractmethod
    def verify(
        self, ctx: PluginContext, reports: list[DisasterReport]
    ) -> tuple[list[DisasterReport], list[DisasterReport]]:
        """Split into (confirmed, unverified). Never drop, only label."""


class MatcherPlugin(BasePlugin):
    @abstractmethod
    def rank(
        self, ctx: PluginContext, query: UserQuery, resources: list[Resource]
    ) -> list[RankedResult]:
        """Weighted rank: dist + trust + capacity + freshness."""


class RouterPlugin(BasePlugin):
    @abstractmethod
    def route(
        self, ctx: PluginContext, start: tuple[float, float], end: tuple[float, float], algo: str = "astar"
    ) -> RoutePath:
        """Shortest safe path. algo in {dijkstra, astar}."""
