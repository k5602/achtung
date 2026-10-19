# Achtung "college project"

Real-time disaster info + relief matching. KFS prototype. Intro to Algorithms course.

## Run

```bash
uv sync --group dev
uv run achtung                                          # opens the TUI
uv run achtung --cli --need all --text "اكل في كفر الشيخ"  # plain output
uv run achtung --cli --debug                           # plain output + plugin logs
uv run pytest -q
```

## Flags

| Flag | Default | What it does |
|---|---|---|
| `--need` | `all` | `food` \| `shelter` \| `medical` \| `water` \| `all` |
| `--text` | `اكل في كفر الشيخ` | query text |
| `--cli` | off | plain output instead of the TUI |
| `--debug` | off | verbose plugin logs (verifier confirmations) |

## Layout

- `src/achtung/core/` — frozen contracts: models, base, store, registry, geo
- `src/achtung/plugins/{collector,retrieval,verifier,matcher,router,evaluator}/` — one owner each
- `src/achtung/tui.py`: Textual TUI over the pipeline (query box + four panels + eval status)
- `src/achtung/data/` — `kfs_mock.json`, `kfs_graph.json` (OSM-derived), synonyms
- `tests/` — contract + distance + pipeline

## Owners

| Plugin | Member | TODO |
|---|---|---|
| collector | P1 | live API parsing |
| retrieval | P2 | BM25 upgrade |
| verifier | P3 | threshold tuning |
| matcher | P4 | weight search |
| router | P5 | road closures |
| evaluator | yahia | TUI status metrics |

Rule: `core/models.py` frozen after hour 2. Plugins talk via `store` only.
