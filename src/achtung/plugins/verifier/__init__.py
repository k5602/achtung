"""P3 verifier: trust filter. Owner: P3.

Splits reports into (confirmed, unverified) via
source trust table + threshold. Never drops items,
only labels. Guards everything downstream.
Takes ctx (shared context object passed to every plugin).
"""
from achtung.plugins.verifier.plugin import Verifier

__all__ = ["Verifier"]
