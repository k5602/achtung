"""Shared context passed to every plugin."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from achtung.core.store import InMemoryStore

LogFn = Callable[[str], None]


@dataclass
class PluginContext:
    store: InMemoryStore
    config: dict[str, Any] = field(default_factory=dict)
    log: LogFn = print  # swap in tests
