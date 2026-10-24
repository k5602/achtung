"""One-screen TUI: trusted news, warnings, nearest aid, road."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import ClassVar

from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Footer, Header, Select, Static

from achtung.core.context import PluginContext
from achtung.core.models import DisasterReport, RankedResult, RoutePath
from achtung.core.registry import get
from achtung.main import KFS_LAT, KFS_LON, NEEDS, build_ctx

MAX_REPORTS = 6
MAX_AID = 8

NEED_LABELS = {
    "food": "Food اكل",
    "water": "Water مياه",
    "shelter": "Shelter ملجأ",
    "medical": "Medical دواء",
    "all": "All الكل",
}


@dataclass
class PipelineResult:
    """What the screen shows: counts plus the data behind each panel."""

    need: str
    collected: int = 0
    hits: list[DisasterReport] = field(default_factory=list)
    confirmed: list[DisasterReport] = field(default_factory=list)
    unverified: list[DisasterReport] = field(default_factory=list)
    ranked: list[RankedResult] = field(default_factory=list)
    route: RoutePath | None = None

    @property
    def best(self) -> RankedResult | None:
        """Top ranked aid point."""
        return self.ranked[0] if self.ranked else None


def run_pipeline(ctx: PluginContext) -> PipelineResult:
    """Run the 5 plugins in order: collect, search, verify, rank, route."""
    query = ctx.config["query"]
    result = PipelineResult(need=query.need)
    get("collector").run(ctx)
    result.collected = len(ctx.store.reports)
    result.hits = get("retrieval").search(ctx, query)
    result.confirmed, result.unverified = get("verifier").verify(ctx, result.hits)
    result.ranked = get("matcher").rank(ctx, query, ctx.store.resources)

    best = result.best
    if best is not None:
        result.route = get("router").route(
            ctx, (KFS_LAT, KFS_LON), (best.resource.lat, best.resource.lon)
        )
    return result


class AchtungApp(App):
    """Four panels over the pipeline; the need selector reruns it."""

    TITLE = "Achtung - SafeReach"
    BINDINGS: ClassVar[list[BindingType]] = [Binding("q", "quit", "quit")]

    CSS = """
    #status { height: 1; padding: 0 1; }
    #panels { height: 1fr; }
    .col { width: 1fr; padding: 0 1; }
    """

    def __init__(self, ctx: PluginContext | None = None) -> None:
        super().__init__()
        self.ctx = ctx or build_ctx()
        self.result = run_pipeline(self.ctx)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(id="status")
        with Horizontal(id="panels"):
            with VerticalScroll(classes="col"):
                yield Static(id="confirmed")
                yield Static(id="unverified")
            with VerticalScroll(classes="col"):
                yield Static(id="aid")
                yield Static(id="road")
        yield Select(
            [(NEED_LABELS[n], n) for n in NEEDS],
            value=self.ctx.config["query"].need,
            prompt="pick a need",
            allow_blank=False,
            id="query",
        )
        yield Footer()

    def on_mount(self) -> None:
        self._render_screen()
        self.query_one("#query", Select).focus()

    def on_select_changed(self, event: Select.Changed) -> None:
        need = str(event.value)
        if need not in NEEDS:
            return
        self.ctx.config["query"] = replace(self.ctx.config["query"], need=need)
        self.result = run_pipeline(self.ctx)
        self._render_screen()

    def _render_screen(self) -> None:
        r = self.result
        self.sub_title = f"KFS University | need: {NEED_LABELS.get(r.need, r.need)}"
        self.query_one("#status", Static).update(self._status_line(r))
        self.query_one("#confirmed", Static).update(
            self._reports_table("Trusted news", r.confirmed, "green")
        )
        self.query_one("#unverified", Static).update(
            self._reports_table("Warnings - rumors kept", r.unverified, "yellow")
        )
        self.query_one("#aid", Static).update(self._aid_table(r))
        self.query_one("#road", Static).update(self._road_panel(r))

    @staticmethod
    def _status_line(r: PipelineResult) -> Text:
        line = Text()
        line.append(f"{r.collected} reports  ", style="dim")
        line.append(f"{len(r.hits)} matches  ", style="green")
        line.append(f"{len(r.confirmed)} trusted  ", style="green")
        line.append(f"{len(r.unverified)} unverified  ", style="yellow")
        line.append(f"{len(r.ranked)} aid points  ", style="cyan")
        if r.route is not None:
            line.append(f"route {r.route.distance_km:.1f} km", style="blue")
        return line

    @staticmethod
    def _reports_table(title: str, reports: list[DisasterReport], color: str) -> Table:
        shown = reports[:MAX_REPORTS]
        count = str(len(reports))
        if len(shown) != len(reports):
            count = f"{len(reports)}, top {len(shown)}"
        table = Table(
            title=f"{title} ({count})",
            title_justify="left",
            title_style=f"bold {color}",
            expand=True,
            border_style="dim",
            padding=(0, 1),
        )
        table.add_column("source", style="dim", no_wrap=True, max_width=18, ratio=2)
        table.add_column("trust", justify="right", width=5)
        table.add_column("text", no_wrap=True, overflow="ellipsis", ratio=3)
        for rep in shown:
            table.add_row(escape(rep.source), f"{rep.trust:.2f}", escape(rep.text))
        if not shown:
            table.add_row("-", "-", "nothing yet")
        return table

    @staticmethod
    def _aid_table(r: PipelineResult) -> Table:
        shown = r.ranked[:MAX_AID]
        count = str(len(r.ranked))
        if len(shown) != len(r.ranked):
            count = f"{len(r.ranked)}, top {len(shown)}"
        table = Table(
            title=f"Nearest aid ({count})",
            title_justify="left",
            title_style="bold cyan",
            expand=True,
            border_style="dim",
            padding=(0, 1),
        )
        table.add_column("name", no_wrap=True, overflow="ellipsis", ratio=3)
        table.add_column("kind", width=8, no_wrap=True)
        table.add_column("km", justify="right", width=6)
        table.add_column("score", justify="right", width=6)
        for item in shown:
            table.add_row(
                escape(item.resource.name),
                item.resource.kind,
                f"{item.distance_km:.1f}",
                f"{item.score:.2f}",
            )
        if not shown:
            table.add_row("-", "-", "-", "-")
        return table

    @staticmethod
    def _road_panel(r: PipelineResult) -> Panel:
        best = r.best
        target = best.resource.name if best else "no aid point yet"
        if r.route is None:
            body = Text("no route", style="yellow")
        else:
            body = Text()
            body.append(f"{r.route.algo}: {r.route.distance_km:.1f} km, ")
            body.append(f"{len(r.route.nodes)} nodes, {r.route.expanded} expanded\n", style="dim")
            body.append(" -> ".join(r.route.nodes), style="dim")
        return Panel(body, title=f"Road to {target}", title_align="left", border_style="blue")
