"""Plugin registry wiring. Import here to register."""
from achtung.core.registry import PLUGINS, get, register, run_all
from achtung.plugins.collector import Collector
from achtung.plugins.matcher import Matcher
from achtung.plugins.retrieval import Retrieval
from achtung.plugins.router import Router
from achtung.plugins.verifier import Verifier

register(Collector())
register(Retrieval())
register(Verifier())
register(Matcher())
register(Router())

__all__ = [
           "PLUGINS",
           "Collector",
           "Matcher",
           "Retrieval",
           "Router",
           "Verifier",
           "get",
           "register",
           "run_all",
]
