#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Multi-arm scoring harness skeleton (protocol-pending).

The four concepts this harness honors — states with precedence, coverage
identity as a gate, handoff fields, staleness propagation to descendants —
are the ones the collaborating lab adopted from the September forum posts.
They are implemented here as they were specified there, not re-invented.

Protocol-independent by design: the rubric and arm definitions plug in when
the draft protocol arrives. Fail-closed everywhere: an arm cannot run
unpinned, a case cannot load without its provenance, and an export cannot
leave with a non-opaque identifier.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

# ---- the four states, with precedence (lowest to highest) ----
# A record is in exactly one state; the highest applicable state wins.
STATE_PRECEDENCE = ["FRESH", "STALE", "BLOCKED", "ZERO_VETO"]
STATE_RANK = {s: i for i, s in enumerate(STATE_PRECEDENCE)}


def resolve_state(states: list[str]) -> str:
    """Precedence resolution: the highest-precedence state wins."""
    valid = [s for s in states if s in STATE_RANK]
    if not valid:
        raise ValueError(f"no known states in {states}")
    return max(valid, key=lambda s: STATE_RANK[s])


# ---- staleness propagation to descendants ----
def propagate_staleness(nodes: dict[str, dict], edges: list[tuple[str, str]]) -> None:
    """A stale node makes every descendant stale (never the reverse).

    The traversal is STRUCTURAL: it follows the edge graph regardless of the
    intermediate nodes' states, so a FRESH descendant behind a BLOCKED
    intermediate is still reached. Precedence is respected at each node: a
    descendant already BLOCKED or ZERO_VETO keeps its higher-precedence
    state; anything below STALE is raised to STALE with its source recorded.
    """
    children: dict[str, list[str]] = {}
    for parent, child in edges:
        children.setdefault(parent, []).append(child)
    frontier = [n for n, meta in nodes.items() if meta.get("state") == "STALE"]
    visited: set[str] = set()
    while frontier:
        nxt = frontier.pop()
        for child in children.get(nxt, []):
            if child in visited:
                continue
            visited.add(child)
            nodes[child]["stale_from"] = nxt
            if STATE_RANK[nodes[child].get("state", "FRESH")] < STATE_RANK["STALE"]:
                nodes[child]["state"] = "STALE"
            frontier.append(child)


# ---- coverage identity as a gate ----
def coverage_identity(covered: set[str], required: set[str]) -> str:
    """The gate: a case is admissible only under an exact coverage identity.
    Partial coverage is BLOCKED, never silently passed."""
    missing = required - covered
    extra = covered - required
    if missing:
        return f"BLOCKED:missing={sorted(missing)}"
    if extra:
        return f"BLOCKED:extra={sorted(extra)}"
    return "ADMITTED"


# ---- handoff fields ----
HANDOFF_FIELDS = ("case_id", "arm", "state", "coverage", "scored_at", "harness_sha")


@dataclass(frozen=True)
class ArmDeclaration:
    """One arm of the study, declared in code and versioned."""
    arm_id: str
    description: str
    scorer: Callable[[dict], dict]          # plugs in from the protocol
    export_fields: tuple[str, ...]          # must be a subset of protocol fields
    version: str


@dataclass
class FixtureProvenance:
    """No fixture loads without provenance; no import before the license check.

    The schema matches the collaboration correspondence (A. Vidal-Gadea,
    2026-11-06): each fixture is a versioned artifact with a source revision
    and a transformation history, and the license is established BEFORE
    anything is imported (the AGPL/GPL lesson).
    """
    source: str
    license: str
    source_revision: str
    transformation_history: tuple[str, ...] = field(default=())

    def admits_import(self) -> bool:
        return self.license.upper() in {
            "CC0-1.0", "CC-BY-4.0", "MIT", "APACHE-2.0", "BSD-3-CLAUSE", "ISC"}

    def to_record(self) -> dict:
        """The provenance record that travels with the fixture declaration."""
        return {"source": self.source, "license": self.license,
                "source_revision": self.source_revision,
                "transformation_history": list(self.transformation_history)}


def harness_sha(paths: list[Path]) -> str:
    """The pin: a deterministic hash over the harness's own source, reviewed
    and pinned by the running site before any arm executes."""
    digest = hashlib.sha256()
    for p in sorted(paths):
        digest.update(p.name.encode())
        digest.update(hashlib.sha256(p.read_bytes()).digest())
    return digest.hexdigest()


def export_gate(rows: list[dict], allowed: set[str]) -> list[dict]:
    """Every exported row carries only opaque tokens and allowed fields.
    Fail-closed: an unknown field or a non-opaque identifier blocks the export.

    `allowed` declares the export schema, including STRUCTURAL fields (arm,
    condition, block, segment - "the analysis is only feasible if the table
    carries more than scores", per the collaboration correspondence). The
    gate enforces the declared schema exactly: every allowed field must be
    present in every row, and no undeclared field may ride along.
    """
    out = []
    for row in rows:
        missing = allowed - set(row)
        if missing:
            raise ValueError(f"export blocked: missing declared fields {sorted(missing)}")
        extra = set(row) - allowed
        if extra:
            raise ValueError(f"export blocked: fields {sorted(extra)}")
        cid = str(row.get("case_id", ""))
        if not cid or not cid.replace("-", "").replace("_", "").isalnum():
            raise ValueError(f"export blocked: non-opaque case_id {cid!r}")
        out.append({k: row[k] for k in row})
    return out
