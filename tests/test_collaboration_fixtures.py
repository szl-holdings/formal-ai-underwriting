"""Collaboration fixture package: the six named failure classes.

Proof boundary: these are SYNTHETIC fixtures. Passing demonstrates gate
behavior only — nothing about any biological measurement (the reciprocal
honesty clause, agreed in the correspondence).

Executable homes: four classes are enforced by THIS harness (stale
identifier, conflicting identifier, undeclared field/unit disagreement,
missing-evidence fail-closed). The truncated-tool-result and
namespace-collision fixtures carry declared expected verdicts whose
executable home is the szl-forge grounding gate (training/distill/
distill_wave.py); they are specified here with provenance so the
collaboration's shared fixture package is complete in one place.
"""
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "harness" / "scoring"))
from harness import FixtureProvenance, propagate_staleness, resolve_state, export_gate  # noqa: E402

FIXTURES = json.loads((ROOT / "harness" / "scoring" / "fixtures" / "fixtures.json").read_text())


def fixture(fid):
    return next(f for f in FIXTURES["fixtures"] if f["id"] == fid)


def test_package_has_six_fixtures_all_provenanced():
    assert len(FIXTURES["fixtures"]) == 6
    classes = set()
    for f in FIXTURES["fixtures"]:
        p = FixtureProvenance(**f["provenance"])
        assert p.admits_import(), f["id"]  # license check before import
        assert f["expected"]
        classes.add(f["failure_class"])
    assert classes == {"stale_identifier", "conflicting_identifier",
                       "truncated_tool_result", "namespace_collision",
                       "undeclared_field_unit_disagreement",
                       "missing_required_evidence"}


def test_fx_stale_identifier():
    f = fixture("fx-stale-identifier")["case"]
    nodes = {k: dict(v) for k, v in f["nodes"].items()}
    propagate_staleness(nodes, [tuple(e) for e in f["edges"]])
    assert nodes["entry-1"]["state"] == "STALE"


def test_fx_conflicting_identifier():
    f = fixture("fx-conflicting-identifier")["case"]
    assert resolve_state(f["states"]) == f["expected_state"] == "BLOCKED"


def test_fx_field_unit_disagreement_blocks_export():
    f = fixture("fx-field-unit-disagreement")["case"]
    with pytest.raises(ValueError, match="export blocked"):
        export_gate([f["row"]], set(f["declared_fields"]))


def test_fx_missing_evidence_fails_closed():
    """A cluster excluded without a reason is the fail-closed evidence case:
    required evidence missing => validation error, never a silent pass."""
    f = fixture("fx-missing-evidence-fail-closed")["case"]
    from _queue_snapshot_vendored import SnapshotError, validate, SCHEMA_VERSION
    snapshot = {"schema_version": SCHEMA_VERSION,
                "clustering": {"primary_key": "shared_assignment_interference_unit",
                               "assignment_unit": "batch-slot",
                               "interference_unit": "batch-slot",
                               "carryover_rule": "carryover_crossing_the_unit_requires_a_broader_cluster_declaration_before_randomization",
                               "queue_entry_ids_are": "separate_observations"},
                "cluster_roster": [f["cluster"]],
                "queue_entries": []}
    with pytest.raises(SnapshotError, match="explicit reason"):
        validate(snapshot)


def test_gate_home_fixtures_carry_expected_verdicts():
    """The truncated and namespace-collision fixtures declare their expected
    verdicts and their executable home (the szl-forge grounding gate)."""
    trunc = fixture("fx-truncated-tool-result")
    assert "TRUNCATED_GENERATION" in trunc["expected"]
    ns = fixture("fx-namespace-collision")
    assert "REJECT" in ns["expected"]
