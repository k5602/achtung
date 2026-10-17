"""P3 verifier: confirmed vs unverified split. Owner: P3."""
from __future__ import annotations

from dataclasses import replace

from achtung.core.base import VerifierPlugin
from achtung.core.context import PluginContext
from achtung.core.models import DisasterReport

TRUST = { "Egyptian Red Crescent - Kafr El-Sheikh branch": 0.9,
         "Egyptian Red Crescent - Desouk branch": 0.85,
         "Kafr El-Sheikh Governorate": 0.9,
         "United Nations - WFP" : 0.95,
         "United Nations - UNHCR" : 0.95,
         "Resala NGO - Kafr El-Sheikh": 0.75,
         "Al-Ahram news": 0.6,
         "Facebook post": 0.3,
         "WhatsApp forward": 0.2,
         "TikTok video": 0.25,
         }
THRESHOLD = 0.6
class Verifier(VerifierPlugin):
    name = "verifier"
    def setup(self, ctx: PluginContext) -> None:
        """stateless"""
    def run(self, ctx: PluginContext) -> tuple[list[DisasterReport], list[DisasterReport]]:
        """Verify everything currently in store."""
        return self.verify(ctx,ctx.store.reports)
    def score(self, report: DisasterReport) -> float:
        """Trust score 0..1."""
        return TRUST.get(report.source, 0.0)
    def verify(
        self, ctx: PluginContext, reports: list[DisasterReport]
    ) -> tuple[list[DisasterReport], list[DisasterReport]]:
        """Split only. Never drop."""
        confirmed: list[DisasterReport] = []
        unverified: list[DisasterReport] = []
        for report in reports:
            is_confirmed = self.score(report) >= THRESHOLD
            report = replace(report, verified=is_confirmed)
            if is_confirmed:
                confirmed.append(report)
            else:
                unverified.append(report)
        ctx.log(
            f"Verifier: {len(confirmed)} confirmed, "
            f"{len(unverified)} unverified"
        )
        return confirmed, unverified