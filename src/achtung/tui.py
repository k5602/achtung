"""One-screen TUI: trusted news, warnings, nearest aid, road."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar, Protocol

from rich.console import Group
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Input, Static
from textual.worker import WorkerCancelled, WorkerFailed

from achtung.core.context import PluginContext
from achtung.core.models import DisasterReport, EvaluateResult, RankedResult, RoutePath, UserQuery
from achtung.core.registry import get
from achtung.main import KFS_LAT, KFS_LON, build_ctx

MAX_REPORTS = 6
MAX_AID = 8
STEPS_PER_KM = 1300


class EvaluatorLike(Protocol):
    """Just to Injected into the app, and accept the protocol i defined"""

    def evaluate(self, ctx: PluginContext, query: UserQuery) -> EvaluateResult: ...

    @property
    def results(self) -> list[EvaluateResult]: ...


@dataclass
class PipelineResult:
    """What the screen shows: counts plus the data behind each panel."""

    text: str
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


class BenchmarkScreen(ModalScreen[None]):
    """ctrl+b: full benchmark status for every query in the session."""

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("ctrl+b", "close", "close"),
        Binding("escape", "close", "close"),
    ]
    CSS = """
    BenchmarkScreen { align: center middle; }
    #bench {
        width: 96%; height: 92%;
        border: round green; background: $surface; padding: 1 2;
    }
    """

    def __init__(self, results: list[EvaluateResult]) -> None:
        super().__init__()
        self.results = results

    def compose(self) -> ComposeResult:
        yield VerticalScroll(Static(self._body(), id="bench"))

    def action_close(self) -> None:
        self.dismiss()

    def _body(self) -> Group:
        if not self.results:
            return Group(Text("no queries evaluated yet", style="dim"))
        last = self.results[-1]

        head = Text()
        head.append(f'last query: "{last.text}"', style="bold")
        head.append(f"  need={last.need}  runs={last.runs}\n", style="dim")

        timing = Table(
            title=f"timing (mean of {last.runs} runs)",
            title_justify="left",
            title_style="bold",
            expand=True,
            border_style="dim",
            padding=(0, 1),
        )
        timing.add_column("stage")
        timing.add_column("mean ms", justify="right")
        timing.add_column("min ms", justify="right")
        timing.add_column("max ms", justify="right")
        timing.add_row("retrieval", f"{last.retrieval_ms:.3f}", "-", "-")
        timing.add_row("verify", f"{last.verify_ms:.3f}", "-", "-")
        timing.add_row("match", f"{last.match_ms:.3f}", "-", "-")
        route = "-" if last.route_ms is None else f"{last.route_ms:.3f}"
        timing.add_row("route", route, "-", "-")
        timing.add_row(
            "total",
            f"{last.total_ms:.3f}",
            f"{last.total_min_ms:.3f}",
            f"{last.total_max_ms:.3f}",
        )

        meta = Text()
        meta.append("ranking: ", style="dim")
        meta.append(
            f"baseline {last.baseline_top1} -> weighted {last.weighted_top1} "
        )
        meta.append(
            "agree" if last.top1_agree else "MISMATCH",
            style="green" if last.top1_agree else "red",
        )
        meta.append(f"  swap={last.swap}  hits={last.hits}\n") # end of first line .
        meta.append("routing: ", style="dim")
        if last.dijkstra_km is None or last.astar_km is None:
            meta.append("no route benchmarked", style="yellow")
        else:
            meta.append(
                f"dijkstra {last.dijkstra_km:.3f} km / {last.dijkstra_expanded} "
                f"expanded | astar {last.astar_km:.3f} km / {last.astar_expanded} expanded"
            )
        meta.append("\n")

        history = Table(
            title=f"history ({len(self.results)} queries)",
            title_justify="left",
            title_style="bold cyan",
            expand=True,
            border_style="dim",
            padding=(0, 1),
        )
        history.add_column("#", justify="right", width=3)
        history.add_column("query", no_wrap=True, overflow="ellipsis", ratio=3)
        history.add_column("need", width=6, no_wrap=True)
        history.add_column("mean", justify="right", width=7)
        history.add_column("min-max", justify="right", width=13)
        history.add_column("hits", justify="right", width=4)
        history.add_column("top1", justify="center", width=5)
        history.add_column("swap", justify="right", width=4)
        history.add_column("d-km", justify="right", width=6)
        history.add_column("a-km", justify="right", width=6)
        for i, res in enumerate(self.results, 1):
            dkm = "-" if res.dijkstra_km is None else f"{res.dijkstra_km:.2f}"
            akm = "-" if res.astar_km is None else f"{res.astar_km:.2f}"
            history.add_row(
                str(i),
                escape(res.text),
                res.need,
                f"{res.total_ms:.3f}",
                f"{res.total_min_ms:.3f}-{res.total_max_ms:.3f}",
                str(res.hits),
                "ok" if res.top1_agree else "X",
                str(res.swap),
                dkm,
                akm,
            )
        return Group(
            head,
            timing,
            meta,
            history,
            Text("ctrl+b / esc to close", style="dim"),
        )


def run_pipeline(ctx: PluginContext) -> PipelineResult:
    """Run the 5 plugins in order: collect, search, verify, rank, route."""
    query = ctx.config["query"]
    result = PipelineResult(text=query.text)

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
    """KFS query box on top, four panels below, Enter reruns the pipeline."""

    TITLE = "Achtung - SafeReach"
    BINDINGS: ClassVar[list[Binding]] = [
        Binding("q", "quit", "quit"),
        Binding("ctrl+b", "open_benchmark", "benchmark"),
    ]

    CSS = """
    #status { height: 1; padding: 0 1; }
    #panels { height: 1fr; }
    .col { width: 1fr; padding: 0 1; }
    """

    def __init__(
        self,
        ctx: PluginContext | None = None,
        evaluator: EvaluatorLike | None = None,
    ) -> None:
        super().__init__()
        self.ctx = ctx or build_ctx()
        self.evaluator = evaluator
        self.eval_result: EvaluateResult | None = None
        self.need = self.ctx.config["query"].need
        self.debug_logs = bool(self.ctx.config.get("debug"))
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
        yield Input(placeholder="type a query, Enter to run", id="query")
        yield Footer()

    async def on_mount(self) -> None:
        self._render_screen()
        self.query_one("#query", Input).focus()
        await self._evaluate_and_refresh()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return
        self.ctx = build_ctx(self.need, text, debug=self.debug_logs)
        self.result = run_pipeline(self.ctx)
        self._render_screen()
        await self._evaluate_and_refresh()

    async def _evaluate_and_refresh(self) -> None:
        """Run the injected evaluator off the event loop, then repaint."""
        if self.evaluator is None:
            return
        try:
            query: UserQuery = self.ctx.config["query"]
            self.eval_result = await self._evaluate_worker(self.ctx, query).wait()
        except (WorkerCancelled, WorkerFailed):
            return
        self._render_screen()

    def action_open_benchmark(self) -> None:
        """ctrl+b: full benchmark status for all queries this session."""
        results = list(self.evaluator.results) if self.evaluator is not None else []
        self.push_screen(BenchmarkScreen(results))

    # perform the evaluator on separated Thread .
    @work(thread=True, exclusive=True, group="evaluate", exit_on_error=False)
    def _evaluate_worker(self, ctx: PluginContext, query: UserQuery) -> EvaluateResult:
        """Blocking timing work runs in a thread; UI stays responsive."""
        assert self.evaluator is not None
        return self.evaluator.evaluate(ctx, query)

    def _render_screen(self) -> None:
        r = self.result
        self.sub_title = f'KFS University | "{r.text}"'
        self.query_one("#status", Static).update(self._status_line(r, self.eval_result))
        self.query_one("#confirmed", Static).update(
            self._reports_table("Trusted news", r.confirmed, "green")
        )
        self.query_one("#unverified", Static).update(
            self._reports_table("Warnings - rumors kept", r.unverified, "yellow")
        )
        self.query_one("#aid", Static).update(self._aid_table(r))
        self.query_one("#road", Static).update(self._road_panel(r))

    @staticmethod
    def _status_line(
        r: PipelineResult, eval_result: EvaluateResult | None = None
    ) -> Text:
        line = Text()
        line.append(f"{r.collected} reports  ", style="dim")
        line.append(f"{len(r.hits)} matches  ", style="green")
        line.append(f"{len(r.confirmed)} trusted  ", style="green")
        line.append(f"{len(r.unverified)} unverified  ", style="yellow")
        line.append(f"{len(r.ranked)} aid points  ", style="cyan")
        if r.route is not None:
            line.append(f"route {r.route.distance_km:.1f} km", style="blue")
        if eval_result is not None:
            line.append(
                f"  eval {eval_result.total_ms:.2f}ms "
                f"({eval_result.total_min_ms:.2f}-{eval_result.total_max_ms:.2f}, "
                f"{eval_result.runs} runs)",
                style="dim",
            )
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
            steps = round(r.route.distance_km * STEPS_PER_KM)
            body.append(f"{r.route.algo}: {r.route.distance_km:.1f} km")
            body.append(f"  ~{steps:,} steps\n", style="dim")
            body.append(" -> ".join(r.route.nodes), style="dim")
        return Panel(body, title=f"Road to {target}", title_align="left", border_style="blue")
