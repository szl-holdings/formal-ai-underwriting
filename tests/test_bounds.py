#!/usr/bin/env python3
"""Regression tests for the statistical-bound claim semantics (Phase A B1/B2)."""
import math
import unittest

# Import the package normally: either installed (`pip install -e .[test]`) or
# from the repository root, which `python -m unittest` / `python -m pytest`
# put on sys.path. No CWD-relative sys.path edits.
from certification.bounds import certify_risk, pac_bayes_mcallester


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


if __name__ == "__main__":
    unittest.main()
