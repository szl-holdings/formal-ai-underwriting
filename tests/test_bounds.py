#!/usr/bin/env python3
"""Regression tests for the statistical-bound claim semantics (Phase A B1/B2)."""
import json
import math
import subprocess
import sys
import unittest
from pathlib import Path

# Import the package normally: either installed (`pip install -e .[test]`) or
# from the repository root, which `python -m unittest` / `python -m pytest`
# put on sys.path. No CWD-relative sys.path edits.
from certification.bounds import certify_risk, hoeffding_tail, pac_bayes_mcallester

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestBoundSemantics(unittest.TestCase):
    def test_kl_monotone_increasing(self):
        # B1: the bound must never tighten as KL grows
        b = [pac_bayes_mcallester(0.02, kl, 100, 0.05)["bound"] for kl in (0.0, 0.1, 1.0)]
        self.assertTrue(b[0] < b[1] < b[2])

    def test_interpretation_no_false_tightening_claim(self):
        # B1: the old text claimed "a tighter bound requires the measured KL"
        r = certify_risk(errors=2, n=100, delta=0.05)
        self.assertNotIn("a tighter bound requires", r["interpretation"])
        self.assertIn("monotonically increasing in KL", r["interpretation"])

    def test_kl0_looser_than_hoeffding(self):
        # B2: PAC KL=0 is looser than Hoeffding for all n >= 1
        for n in (8, 100, 10_000):
            r = certify_risk(errors=max(1, n // 50), n=n, delta=0.05)
            self.assertGreater(r["pac_bayes_bound_kl0"], r["hoeffding_bound"])

    def test_pac_bayes_can_beat_hoeffding_only_with_structural_kl(self):
        # the honest condition: KL + ln(2*sqrt(n)/delta) < ln(1/delta)
        n, delta = 100, 0.05
        small_kl = 0.0
        self.assertGreater(small_kl + math.log(2 * math.sqrt(n) / delta),
                           math.log(1.0 / delta))


class TestBoundArithmetic(unittest.TestCase):
    def test_hoeffding_bound_matches_closed_form(self):
        # true risk <= emp + sqrt(ln(1/delta) / (2n)) with confidence 1 - delta
        r = certify_risk(errors=3, n=48, delta=0.05)
        expected = 3 / 48 + math.sqrt(math.log(1 / 0.05) / (2 * 48))
        self.assertAlmostEqual(r["hoeffding_bound"], expected, places=12)
        # the tail probability at that t is exactly delta
        self.assertAlmostEqual(r["hoeffding_detail"]["bound"], 0.05, places=12)
        self.assertAlmostEqual(r["confidence"], 0.95, places=12)

    def test_pac_bayes_never_tighter_than_hoeffding_for_any_kl(self):
        # KL >= 0 and ln(2*sqrt(n)/delta) > ln(1/delta) for n >= 1, so on the
        # same empirical risk the PAC-Bayes value always exceeds Hoeffding.
        for n in (8, 48, 100, 10_000):
            for delta in (0.01, 0.05, 0.2):
                hoeff_slack = math.sqrt(math.log(1 / delta) / (2 * n))
                for emp in (0.0, 0.02, 0.5):
                    for kl in (0.0, 0.1, 1.0, 10.0):
                        pac = pac_bayes_mcallester(emp, kl, n, delta)["bound"]
                        self.assertGreater(pac, emp + hoeff_slack, (n, delta, emp, kl))


class TestFailClosed(unittest.TestCase):
    def test_certify_risk_rejects_invalid_delta(self):
        # delta=0 used to raise ZeroDivisionError and delta>1 / <0 / inf a bare
        # "math domain error"; all must be a clear ValueError before any maths.
        for delta in (0, 0.0, 1, 1.0, 1.5, -0.1, math.nan, math.inf, -math.inf, True, "0.05", None):
            with self.subTest(delta=delta), self.assertRaises(ValueError):
                certify_risk(errors=3, n=48, delta=delta)

    def test_certify_risk_rejects_non_int_n(self):
        for n in (48.0, True, "48", None):
            with self.subTest(n=n), self.assertRaises(ValueError):
                certify_risk(errors=3, n=n)

    def test_certify_risk_rejects_bad_counts(self):
        for errors, n in ((-1, 48), (49, 48), (0, 7), (True, 48)):
            with self.subTest(errors=errors, n=n), self.assertRaises(ValueError):
                certify_risk(errors=errors, n=n)

    def test_hoeffding_tail_rejects_nan_and_negative_t(self):
        # hoeffding_tail(nan, n) used to return a NaN "bound" labelled PROVEN
        for t in (math.nan, -0.1, True, "0.1"):
            with self.subTest(t=t), self.assertRaises(ValueError):
                hoeffding_tail(t, 10)


class TestProvenance(unittest.TestCase):
    def test_proof_status_carried_verbatim_from_atlas(self):
        # szl-holdings/szl-formulas torch-ext/szl_formulas/formula_atlas.v1.json
        # (checked at f4ca3ea): hoeffding_tail -> PROVEN(MomentSubGaussian),
        # pac_bayes_mcallester -> SORRY(PACBayes).
        r = certify_risk(errors=2, n=100, delta=0.05)
        self.assertEqual(r["hoeffding_detail"]["proof_status"], "PROVEN(MomentSubGaussian)")
        self.assertEqual(r["pac_bayes_detail"]["proof_status"], "SORRY(PACBayes)")
        self.assertEqual(r["truth_label"], "MEASURED_STATISTICAL_BOUND")


class TestCommandLine(unittest.TestCase):
    def test_module_cli_prints_certificate(self):
        # the command documented in README.md and templates/certification-report.md
        out = subprocess.run(
            [sys.executable, "-m", "certification.bounds", "3", "48"],
            cwd=REPO_ROOT, check=True, capture_output=True, text=True, timeout=60,
        ).stdout
        cert = json.loads(out)
        self.assertEqual(cert["schema"], "szl.underwriting.risk-bound/v1")
        self.assertEqual(cert["measured"], {"errors": 3, "n": 48, "empirical_risk": 0.0625})
        self.assertAlmostEqual(cert["hoeffding_bound"], certify_risk(3, 48)["hoeffding_bound"], places=12)


if __name__ == "__main__":
    unittest.main()
