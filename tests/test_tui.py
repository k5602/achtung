"""TUI pilot test: changing the need selector reruns the whole pipeline."""
import asyncio

from textual.widgets import Select

from achtung.main import build_ctx
from achtung.tui import AchtungApp


def test_need_switch_reruns_pipeline():
    async def run_case() -> None:
        app = AchtungApp(build_ctx("all"))
        async with app.run_test() as pilot:
            await pilot.pause()
            assert app.ctx.config["query"].need == "all"

            app.query_one("#query", Select).value = "food"
            await pilot.pause()

            assert app.ctx.config["query"].need == "food"
            assert app.result.need == "food"
            assert app.result.hits[0].id == "rep-crescent-01"
            assert "food" in app.sub_title.lower()

    asyncio.run(run_case())
