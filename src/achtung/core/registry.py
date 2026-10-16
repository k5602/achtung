"""Manual plugin registry. No auto-discovery (explicit = fewer conflicts)."""
from __future__ import annotations

from achtung.core.base import BasePlugin
from achtung.core.context import PluginContext

PLUGINS: list[BasePlugin] = []


def register(plugin: BasePlugin) -> BasePlugin:
    """Add plugin once. Called at import of each plugin package."""
    if plugin not in PLUGINS:
        PLUGINS.append(plugin)
    return plugin


def get(name: str) -> BasePlugin:
    """Lookup by plugin.name."""
    for p in PLUGINS:
        if p.name == name:
            return p
    raise KeyError(f"plugin not found: {name}")


def setup_all(ctx: PluginContext) -> None:
    """Call setup on every registered plugin."""
    for p in PLUGINS:
        p.setup(ctx)


def run_all(ctx: PluginContext) -> dict[str, object]:
    """Run all plugins, collect results by name."""
    return {p.name: p.run(ctx) for p in PLUGINS}
