#!/usr/bin/env python3
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
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "harness" / "scoring"))
from harness import FixtureProvenance, propagate_staleness, resolve_state, export_gate  # noqa: E402
from _queue_snapshot_vendored import SnapshotError, validate, SCHEMA_VERSION  # noqa: E402

FIXTURES = json.loads((REPO_ROOT / "harness" / "scoring" / "fixtures" / "fixtures.json").read_text())


def fixture(fid):
    return next(f for f in FIXTURES["fixtures"] if f["id"] == fid)


class TestCollaborationFixtures(unittest.TestCase):
    def test_package_has_six_fixtures_all_provenanced(self):
        self.assertEqual(len(FIXTURES["fixtures"]), 6)
        classes = set()
        for f in FIXTURES["fixtures"]:
            p = FixtureProvenance(**f["provenance"])
            self.assertTrue(p.admits_import(), f["id"])  # license before import
            self.assertTrue(f["expected"])
            classes.add(f["failure_class"])
        self.assertEqual(classes, {"stale_identifier", "conflicting_identifier",
                                    "truncated_tool_result", "namespace_collision",
                                    "undeclared_field_unit_disagreement",
                                    "missing_required_evidence"})

    def test_fx_stale_identifier(self):
        case = fixture("fx-stale-identifier")["case"]
        nodes = {k: dict(v) for k, v in case["nodes"].items()}
        propagate_staleness(nodes, [tuple(e) for e in case["edges"]])
        self.assertEqual(nodes["entry-1"]["state"], "STALE")

    def test_fx_conflicting_identifier(self):
        case = fixture("fx-conflicting-identifier")["case"]
        self.assertEqual(resolve_state(case["states"]), "BLOCKED")

    def test_fx_field_unit_disagreement_blocks_export(self):
        case = fixture("fx-field-unit-disagreement")["case"]
        with self.assertRaises(ValueError):
            export_gate([case["row"]], set(case["declared_fields"]))

    def test_fx_missing_evidence_fails_closed(self):
        """Excluded without a reason: required evidence missing =>
        validation error, never a silent pass."""
        case = fixture("fx-missing-evidence-fail-closed")["case"]
        snapshot = {"schema_version": SCHEMA_VERSION,
                     "clustering": {"primary_key": "shared_assignment_interference_unit",
                                    "assignment_unit": "batch-slot",
                                    "interference_unit": "batch-slot",
                                    "carryover_rule": "carryover_crossing_the_unit_requires_a_broader_cluster_declaration_before_randomization",
                                    "queue_entry_ids_are": "separate_observations"},
                     "cluster_roster": [case["cluster"]],
                     "queue_entries": []}
        with self.assertRaises(SnapshotError):
            validate(snapshot)

    def test_gate_home_fixtures_carry_expected_verdicts(self):
        trunc = fixture("fx-truncated-tool-result")
        self.assertIn("TRUNCATED_GENERATION", trunc["expected"])
        ns = fixture("fx-namespace-collision")
        self.assertIn("REJECT", ns["expected"])


if __name__ == "__main__":
    unittest.main()
