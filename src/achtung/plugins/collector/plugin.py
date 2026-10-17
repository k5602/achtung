"""P1 collector: live APIs with mock fallback. Owner: P1."""
from __future__ import annotations

from pathlib import Path
import requests 
import datetime 
from achtung.core.base import CollectorPlugin
from achtung.core.context import PluginContext
from achtung.core.models import DisasterReport

MOCK = Path(__file__).parent.parent.parent / "data" / "kfs_mock.json"

url_n = "https://eonet.gsfc.nasa.gov/api/v3/events"

class Collector(CollectorPlugin):
    name = "collector"

    def setup(self, ctx: PluginContext) -> None:
        """Load nothing. Must work offline."""
        pass

    def run(self, ctx: PluginContext) -> list[DisasterReport]:
        """Registry entry. Delegate to collect."""
        return self.collect(ctx)
        
    def collect(self, ctx: PluginContext) -> list[DisasterReport]:
        """Try live, fallback to MOCK. Fill ctx.store."""
        try:
            nasa_url = requests.get(url_n,timeout=5)
            collection_list=[]
            if requests.status_codes == 200:
                nasa_json = nasa_url.json()
                nasa_report = nasa_json["events"]
                for event in nasa_report:
                    time = datetime.datetime.fromisoformat(event["geometry"]["date"]) - datetime.datetime.now(datetime.timezone.utc)
                    hours_ago = time.total_seconds()/3600
                    item:dict={"id":event['id'],
                               "source":event["sources"]["url"],
                               "text":event["title"],
                               "kind":event["categories"]["title"],
                               "lat":event["geometry"]["coordinates"][1],
                               "lon" :event["geometry"]["coordinates"][0],
                               "hours_ago":round(hours_ago,2),
                               "trust":0.8,
                               "verified":True
                               }
                    collection_list.append(ctx.store._to_report(item))
                return collection_list
            else:
                ctx.store.clear()
                ctx.store.load_mock(MOCK)
        except requests.exceptions.Timeout:
            ctx.store.clear()
            ctx.store.load_mock(MOCK)
        return ctx.store.reports
