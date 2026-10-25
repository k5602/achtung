"""Manual plugin registry. No auto-discovery (explicit = fewer conflicts)."""
from __future__ import annotations

from typing import Literal, overload

from achtung.core.base import (
    BasePlugin,
    CollectorPlugin,
    MatcherPlugin,
    RetrievalPlugin,
    RouterPlugin,
    VerifierPlugin,
)
from achtung.core.context import PluginContext

PLUGINS: list[BasePlugin] = []


def register(plugin: BasePlugin) -> BasePlugin:
    """Add plugin once. Called at import of each plugin package."""
    if plugin not in PLUGINS:
        PLUGINS.append(plugin)
    return plugin


@overload
def get(name: Literal["collector"]) -> CollectorPlugin: ...


@overload
def get(name: Literal["retrieval"]) -> RetrievalPlugin: ...


@overload
def get(name: Literal["verifier"]) -> VerifierPlugin: ...


@overload
def get(name: Literal["matcher"]) -> MatcherPlugin: ...


@overload
def get(name: Literal["router"]) -> RouterPlugin: ...


def get(name: str) -> BasePlugin:
    """Lookup by plugin.name."""
    for p in PLUGINS:
        if p.name == name:
            return p
    raise KeyError(f"plugin not found: {name}")


def run_all(ctx: PluginContext) -> dict[str, object]:
    """Run all plugins, collect results by name."""
    return {p.name: p.run(ctx) for p in PLUGINS}
