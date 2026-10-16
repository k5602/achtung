# Achtung Architecture

## Big idea

Achtung helps people in a disaster find food, shelter, and medicine.
A user asks a question. The system finds trusted news, picks the best aid
points, and draws a safe road to reach them.

Bad posts (rumors) are never deleted. They are only marked as unverified.

## Parts

There are two parts: `core` and `plugins`.

- `core` = shared rules. Nobody changes this please.
  It holds the data shapes (`models.py`), the plugin rules (`base.py`),
  the shared memory (`store.py`), and the plugin list (`registry.py`).
- `plugins` = the 5 jobs. Each person owns one folder.
  Plugins never talk to each other. They only read and write the store.

## Key words

- `ctx` (the shared context object passed to every plugin).
  It carries everything your plugin needs: the store, settings, and log.
- `ctx.store` (shared memory all plugins read and write).
  It holds two lists: reports and resources.
- `ctx.store.reports` (collected disaster posts, like news items).
- `ctx.store.resources` (aid points list, like food and shelters).
- `UserQuery` (user text + location + need, like "food near me").
- `registry` (the list of all 5 plugins, runs them one by one).

## How it works (step by step)

1. User types a question, like "اكل في كفر الشيخ" "easy as a prototype".
2. Collector (P1) loads posts into `ctx.store.reports`.
3. Retrieval (P2) picks the posts that match the question.
4. Verifier (P3) splits posts into confirmed and unverified.
5. Matcher (P4) picks the best aid points from `ctx.store.resources`.
6. Router (P5) finds the shortest safe road to the best aid point.
7. Screen shows: trusted news, warnings about rumors, nearest aid, road.

Data only flows one way: collector -> retrieval -> verifier ->
matcher -> router. This is why 5 people can work at the same time.

## The 5 plugins

### P1 collector (`plugins/collector/`)

Job: bring posts into the store.
In: settings in `ctx.config`. Out: list of `DisasterReport` in the store.
Reads `data/kfs_mock.json` when offline and we can ignore the online part for now.
To finish: call ReliefWeb and GDACS, then fill the store the same way.

Learn: ReliefWeb API docs (https://apidoc.reliefweb.int),
GDACS homepage (https://www.gdacs.org),
Python `requests` pkg timeout.

### P2 retrieval (`plugins/retrieval/`)

Job: find posts that match the question.
In: `UserQuery` + `ctx.store.reports`. Out: sorted post list.
Method: word count + TF-IDF. Goal: BM25 later.
Uses `data/synonyms_ar_en.json` (Arabic word map).

Learn: TF-IDF (https://en.wikipedia.org/wiki/Tf%E2%80%93idf),
BM25 (https://en.wikipedia.org/wiki/Okapi_BM25).

### P3 verifier (`plugins/verifier/`)

Job: mark each post as confirmed or unverified.
In: post list. Out: two lists `(confirmed, unverified)`.
Method: trust table per source + limit number (0.6).
Rule: never delete a post, only label it.

Learn: simple scoring and threshold checks, no link needed.

### P4 matcher (`plugins/matcher/`)

Job: pick the best aid points for the user.
In: `UserQuery` + `ctx.store.resources`. Out: sorted `RankedResult` list.
Method: mixed score = distance + trust + size + freshness.
Also has `baseline()` (distance only) to compare in the report.
Distance math lives in `core/geo.py`.

Learn: Haversine formula (https://en.wikipedia.org/wiki/Haversine_formula).

### P5 router (`plugins/router/`)

Job: shortest safe road on the map.
In: start and end points. Out: `RoutePath` (roads + km + steps).
Reads `data/kfs_graph.json` (road nodes + km edges).
Method: Dijkstra (simple) vs A* (faster, uses distance guess).

Learn: Dijkstra (https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm),
A* (https://en.wikipedia.org/wiki/A*_search_algorithm).

## Evaluator (`tools/evaluate.py`, stub only)

Job: make numbers for the report.
Compares: search speed, mixed rank vs distance-only rank,
Dijkstra vs A* (km + steps). Owner: whoever finishes first.

## How we work without fights "ISA"

1. Do not change `core/` after hour 2.
2. Only change your own `plugins/<name>/plugin.py` "don't even think of commenting a single line of another plugin".
3. Talk to other plugins only through `ctx.store` "your walki talkie".
4. Test your plugin alone: `uv run pytest -q`.
5. Run the full demo: `uv run achtung`.

## Files map

- `src/achtung/core/` = rules (frozen = immutable).
- `src/achtung/plugins/*/` = your work (one folder per person).
- `src/achtung/data/` = fake KFS posts, roads, word map.
- `tools/evaluate.py` = report numbers (stub till we finish all Ps).
- `tests/` = checks that everything fits together.
