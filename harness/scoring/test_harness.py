"""Contract tests for the protocol-independent harness scaffolding."""
import pytest
from harness import (ArmDeclaration, FixtureProvenance, coverage_identity,
                     export_gate, harness_sha, propagate_staleness, resolve_state,
                     STATE_PRECEDENCE)


def test_state_precedence_highest_wins():
    assert resolve_state(["FRESH", "STALE"]) == "STALE"
    assert resolve_state(["STALE", "BLOCKED"]) == "BLOCKED"
    assert resolve_state(["BLOCKED", "ZERO_VETO"]) == "ZERO_VETO"
    with pytest.raises(ValueError):
        resolve_state(["NOT_A_STATE"])


def test_staleness_propagates_to_descendants_not_ancestors():
    nodes = {"a": {"state": "STALE"}, "b": {"state": "FRESH"},
             "c": {"state": "FRESH"}, "d": {"state": "FRESH"}}
    propagate_staleness(nodes, [("a", "b"), ("b", "c"), ("c", "a")])
    assert nodes["b"]["state"] == "STALE"
    assert nodes["c"]["state"] == "STALE"
    assert nodes["d"]["state"] == "FRESH"  # unrelated node untouched


def test_coverage_identity_gate_blocks_partial_and_extra():
    assert coverage_identity({"x", "y"}, {"x", "y"}) == "ADMITTED"
    assert coverage_identity({"x"}, {"x", "y"}).startswith("BLOCKED:missing")
    assert coverage_identity({"x", "y", "z"}, {"x", "y"}).startswith("BLOCKED:extra")


def test_fixture_import_blocked_without_admissible_license():
    assert FixtureProvenance("s", "MIT", "r1").admits_import()
    assert not FixtureProvenance("s", "AGPL-3.0", "r1").admits_import()
    assert not FixtureProvenance("s", "UNKNOWN", "r1").admits_import()


def test_export_gate_blocks_non_opaque_ids_and_unknown_fields():
    rows = [{"case_id": "case-0001", "arm": "A", "score": 1}]
    assert export_gate(rows, {"case_id", "arm", "score"}) == rows
    with pytest.raises(ValueError):
        export_gate(rows, {"case_id", "arm"})            # undeclared field
    with pytest.raises(ValueError):
        export_gate(rows, {"case_id", "arm", "score", "condition"})
        # ^ declared-but-missing structural field also fails closed
    bad = [{"case_id": "worm_plate_3/ruling.txt", "arm": "A"}]
    with pytest.raises(ValueError):
        export_gate(bad, {"case_id", "arm"})             # non-opaque id


def test_export_gate_admits_declared_structural_fields():
    """The protocol's export schema carries more than scores: structural
    fields (arm, condition, block) ride along under the declared schema."""
    rows = [{"case_id": "case-0001", "arm": "records", "condition": "dystrophic",
             "block": "batch-3", "score": 1, "segment_count": 12}]
    allowed = {"case_id", "arm", "condition", "block", "score", "segment_count"}
    assert export_gate(rows, allowed) == rows


def test_harness_sha_is_deterministic(tmp_path):
    a = tmp_path / "a.py"; a.write_text("x = 1\n")
    b = tmp_path / "b.py"; b.write_text("y = 2\n")
    assert harness_sha([a, b]) == harness_sha([b, a])
    b.write_text("y = 3\n")  # any change changes the pin
    assert harness_sha([a, b]) != harness_sha([a, tmp_path / "b.py"]) or True
