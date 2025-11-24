"""Minimal projection data structures used for demo snapshots."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(slots=True)
class ExecutionPolicy:
    batch_size: int | None = None
    concurrency: str | None = None
    retry_limit: int | None = None


@dataclass(slots=True)
class ProjectionNode:
    id: str
    form: str
    operation: str
    module: str
    parameters: Mapping[str, object] = field(default_factory=dict)
    traits: tuple[str, ...] = ()


@dataclass(slots=True)
class ProjectionEdge:
    source: str
    target: str
    channel: str


@dataclass(slots=True)
class ProjectionNetwork:
    nodes: Sequence[ProjectionNode]
    edges: Sequence[ProjectionEdge]
    entrypoints: Sequence[str]
    sinks: Sequence[str]
    execution_policy: ExecutionPolicy


@dataclass(slots=True)
class ProjectionOrigin:
    workspace_root: str
    orchestrator: str
    git_revision: str | None = None
    extras: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class ProjectionDataBundle:
    id: str
    bundle_type: str
    description: str


@dataclass(slots=True)
class ProjectionResources:
    python_requirements: Sequence[str]
    data_bundles: Sequence[ProjectionDataBundle]


@dataclass(slots=True)
class ProjectionTelemetry:
    events: bool
    metrics: bool
    log_level: str | None = None


@dataclass(slots=True)
class ProjectionSnapshot:
    id: str
    origin: ProjectionOrigin
    network: ProjectionNetwork
    resources: ProjectionResources
    telemetry: ProjectionTelemetry
    description: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def write_snapshot(snapshot: ProjectionSnapshot, path: Path | str) -> Path:
    destination = Path(path)
    payload = snapshot.to_dict()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return destination
