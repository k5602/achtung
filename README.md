# Achtung "college project"

Real-time disaster info + relief matching. KFS prototype. Intro to Algorithms course.

## Run

```bash
uv sync --group dev
uv run achtung                                          # opens the TUI
uv run achtung --cli --need food                        # plain output
uv run python tools/evaluate.py
uv run pytest -q
```

## Layout

- `src/achtung/core/`: frozen contracts, models, base, store, registry, geo
- `src/achtung/plugins/{collector,retrieval,verifier,matcher,router}/`: one owner each
- `src/achtung/tui.py`: Textual TUI over the pipeline (need selector + four panels)
- `src/achtung/data/`: `kfs_mock.json`, `kfs_graph.json` (OSM-derived)
- `tools/evaluate.py`: Dijkstra vs A*, baseline vs weighted (for report)
- `tests/`: contract + distance + pipeline

## Owners

| Plugin | Member | TODO |
|---|---|---|
| collector | P1 | live API parsing |
| retrieval | P2 | map live feed kinds to needs |
| verifier | P3 | threshold tuning |
| matcher | P4 | weight search |
| router | P5 | road closures |
