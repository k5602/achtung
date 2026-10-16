"""P3 verifier: confirmed vs unverified split. Owner: P3."""
from __future__ import annotations

from achtung.core.base import VerifierPlugin
from achtung.core.context import PluginContext
from achtung.core.models import DisasterReport

# TODO(P3): define TRUST table + THRESHOLD = 0.6.


class Verifier(VerifierPlugin):
    name = "verifier"

    def setup(self, ctx: PluginContext) -> None:
        """Stateless."""
        # TODO(P3): implement.
        raise NotImplementedError

    def run(self, ctx: PluginContext) -> tuple[list[DisasterReport], list[DisasterReport]]:
        """Verify everything currently in store."""
        # TODO(P3): implement.
        raise NotImplementedError

    def score(self, report: DisasterReport) -> float:
        """Trust score 0..1."""
        # TODO(P3): implement.
        raise NotImplementedError

    def verify(
        self, ctx: PluginContext, reports: list[DisasterReport]
    ) -> tuple[list[DisasterReport], list[DisasterReport]]:
        """Split only. Never drop."""
        # TODO(P3): implement.
        raise NotImplementedError
