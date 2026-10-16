"""P1 collector: live APIs with mock fallback. Owner: P1."""
from __future__ import annotations

from pathlib import Path
import json
# import requests 

from achtung.core.base import CollectorPlugin
from achtung.core.context import PluginContext
from achtung.core.models import DisasterReport

MOCK = Path(__file__).parent.parent.parent / "data" / "kfs_mock.json"

# url_r = "https://api.reliefweb.int/v2/reports?appname=_" 
# url_g = "https://www.gdacs.org/gdacsapi/api/AdaptiveCard/getevent/data"

# reliefWeb_url =  requests.get(url_r,timeout=5)
# gdacs_url = requests.get(url_g,timeout=5)

class Collector(CollectorPlugin):
    name = "collector"

    def setup(self, ctx: PluginContext) -> None:
        """Load nothing. Must work offline."""
        # TODO(P1): implement.
        raise NotImplementedError

    def run(self, ctx: PluginContext) -> list[DisasterReport]:
        """Registry entry. Delegate to collect."""
        # Is it just a trigger collect func till now?
        # return self.collect(ctx)
        raise NotImplementedError
        
    def collect(self, ctx: PluginContext) -> list[DisasterReport]:
        """Try live, fallback to MOCK. Fill ctx.store."""
        ctx.store.load_mock(MOCK)
        return ctx.store.reports
