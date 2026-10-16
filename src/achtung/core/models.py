"""Shared frozen data models. Freeze after hour 2."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DisasterReport:
    id: str
    source: str
    text: str
    kind: str  # food_aid | relief_center | beneficiary_list | ...
    lat: float
    lon: float
    hours_ago: float
    observed_at: datetime
    trust: float  # 0..1, from source table
    verified: bool  # True = confirmed, False = treat as rumor


@dataclass(frozen=True)
class Resource:
    id: str
    kind: str  # food | shelter | medical | water
    name: str
    lat: float
    lon: float
    capacity: int
    source: str
    trust: float
    verified: bool


@dataclass(frozen=True)
class UserQuery:
    text: str
    lat: float
    lon: float
    need: str  # food | shelter | medical | water | all


@dataclass(frozen=True)
class RankedResult:
    resource: Resource
    score: float
    distance_km: float
    verified: bool


@dataclass(frozen=True)
class RoutePath:
    nodes: tuple[str, ...]
    distance_km: float
    algo: str  # dijkstra | astar
    expanded: int  # nodes expanded, for report comparison
