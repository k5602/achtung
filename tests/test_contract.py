"""Contract test: every plugin respects ABC (interface only)."""
import inspect

import achtung.plugins  # noqa: F401
from achtung.core.base import (
    BasePlugin,
    CollectorPlugin,
    MatcherPlugin,
    RetrievalPlugin,
    RouterPlugin,
    VerifierPlugin,
)
from achtung.core.registry import PLUGINS
from achtung.main import build_ctx

EXPECTED = {"collector", "retrieval", "verifier", "matcher", "router"}
IMPLEMENTED = {"collector", "retrieval", "verifier", "matcher", "router"}  # plugins with real run(), add names here as they land
BASES = {
    "collector": CollectorPlugin,
    "retrieval": RetrievalPlugin,
    "verifier": VerifierPlugin,
    "matcher": MatcherPlugin,
    "router": RouterPlugin,
}


def test_all_registered():
    names = {p.name for p in PLUGINS}
    assert EXPECTED <= names


def test_interface_shape():
    for p in PLUGINS:
        assert isinstance(p, BasePlugin)
        assert isinstance(p, BASES[p.name])
        assert p.health() is True
        assert callable(p.run)
        sig = inspect.signature(p.run)
        assert len(sig.parameters) == 1  # run(ctx) only


def test_stubs_raise():
    ctx = build_ctx()
    for p in PLUGINS:
        if p.name in IMPLEMENTED:
            p.run(ctx)  # must not raise once implemented
            continue

        try:
            p.run(ctx)
        except NotImplementedError:
            continue  # interface only, owner implements
        else:
            raise AssertionError(f"{p.name}.run should raise NotImplementedError until implemented")
