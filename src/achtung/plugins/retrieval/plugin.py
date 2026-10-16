"""P2 retrieval: inverted index + TF-IDF. Owner: P2."""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path

from achtung.core.base import RetrievalPlugin
from achtung.core.context import PluginContext
from achtung.core.models import DisasterReport, UserQuery

SYN = Path(__file__).parent.parent.parent / "data" / "synonyms_ar_en.json"
# Primodial Art
TOKEN = re.compile(r"[\w\u0600-\u06FF]+")


class Retrieval(RetrievalPlugin):
    name = "retrieval"

    def __init__(self) -> None:
        self.syn: dict[str, str] = {}

    def setup(self, ctx: PluginContext) -> None:
        """Load AR-EN map. Index built lazily per search."""
        if SYN.exists():
            self.syn = json.loads(SYN.read_text(encoding="utf-8"))
            self.syn.pop("_note", None)

    def run(self, ctx: PluginContext) -> list[DisasterReport]:
        """Default query from config."""
        return self.search(ctx, ctx.config["query"])

    def normalize(self, text: str) -> list[str]:
        """Phrase replace, tokenize, map synonyms."""
        t = text.lower()
        for k, v in self.syn.items():
            if " " in k and k in t:
                t = t.replace(k, v)
        return [self.syn.get(w, w) for w in TOKEN.findall(t)]

    def search(self, ctx: PluginContext, query: UserQuery) -> list[DisasterReport]:
        """TF-IDF + need boost + trust tiebreak."""
        docs = list(ctx.store.reports)
        if not docs:
            return []
        qt = self.normalize(query.text)
        if query.need != "all":
            qt += self.normalize(query.need)
        if not qt:
            return sorted(docs, key=lambda r: -r.trust)
        toks = [self.normalize(f"{r.text} {r.kind} {r.source}") for r in docs]
        df = Counter(t for dt in toks for t in set(dt))
        idf = {t: math.log((len(docs) + 1) / (df[t] + 1)) + 1 for t in set(qt)}
        out: list[tuple[float, float, DisasterReport]] = []
        for r, dt in zip(docs, toks, strict=True):
            c = Counter(dt)
            s = sum((c[t] / len(dt)) * idf[t] for t in set(qt) if t in c)
            if query.need != "all" and query.need in r.kind:
                s += 1.0
            if s > 0:
                out.append((s, r.trust, r))
        out.sort(key=lambda x: (-x[0], -x[1]))
        return [r for _, _, r in out]
