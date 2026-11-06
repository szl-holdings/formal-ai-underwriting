#!/usr/bin/env python3
"""formal_ai_underwriting.certification.bounds — statistical risk bounds for model certificates.

Cherry-picked from szl-holdings/szl-formulas (formula_atlas.v1.json):
  * pac_bayes_mcallester — PROOF-STATUS: SORRY(PACBayes)
  * hoeffding_tail       — PROOF-STATUS: PROVEN(Hoeffding)

These are the mathematical backbone of the certification product: a model
certificate that carries a computed generalization bound from its measured
evaluation sample, with the formula provenance attached.

Honesty contract:
  * The bound is computed from caller-supplied measured inputs; it certifies
    the arithmetic, not the truth of the inputs.
  * A SORRY proof-status is carried verbatim: the Lean obligation is open.
  * Nothing here claims the model is safe; the bound is one certificate axis
    under the Lambda-spine gate, where a single failed measured check vetoes.

SPDX-License-Identifier: Apache-2.0
Source: szl-holdings/szl-formulas torch-ext/szl_formulas/_formulas.py
"""
from __future__ import annotations

import math
from typing import Any


def _real(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def pac_bayes_mcallester(empirical_risk: float, kl: float, n: int, delta: float) -> dict:
    """R(Q) <= emp_risk + sqrt((KL + ln(2*sqrt(n)/delta)) / (2n)).

    Requires n >= 8 (Maurer 2004), loss in [0,1], kl >= 0, delta in (0,1).
    PROOF-STATUS: SORRY(PACBayes) — carried verbatim from the source atlas.
    """
    for name, v in (("empirical_risk", empirical_risk), ("kl", kl), ("delta", delta)):
        if not _real(v):
            raise ValueError(f"{name} must be a real number (bool is not a number)")
    if not isinstance(n, int) or isinstance(n, bool):
        raise ValueError("n must be an int (sample size)")
    if n < 8:
        raise ValueError("n must be >= 8 (Maurer 2004 validity)")
    if not (0.0 <= empirical_risk <= 1.0):
        raise ValueError("empirical_risk must be in [0,1] (bounded loss)")
    if kl < 0.0:
        raise ValueError("kl must be >= 0")
    if not (0.0 < delta < 1.0):
        raise ValueError("delta must be in (0,1)")
    complexity = (kl + math.log(2.0 * math.sqrt(n) / delta)) / (2.0 * n)
    if not (math.isfinite(complexity) and complexity > 0.0):
        raise ValueError("complexity term must be positive and finite")
    value = empirical_risk + math.sqrt(complexity)
    return {
        "formula": "R(Q) <= R_hat(Q) + sqrt((KL(Q||P) + ln(2*sqrt(n)/delta))/(2n))",
        "inputs": {"empirical_risk": empirical_risk, "kl": kl, "n": n, "delta": delta},
        "bound": value,
        "proof_status": "SORRY(PACBayes)",
        "provenance": "szl-holdings/szl-formulas formula_atlas.v1.json",
    }


def hoeffding_tail(t: float, n: int) -> dict:
    """P(mean - E[X] >= t) <= exp(-2*n*t^2).

    PROOF-STATUS: PROVEN(Hoeffding) — carried verbatim from the source atlas.
    """
    if not _real(t) or t < 0:
        raise ValueError("t must be a non-negative real")
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        raise ValueError("n must be a positive int")
    value = math.exp(-2.0 * n * t * t)
    return {
        "formula": "P(mean - E[X] >= t) <= exp(-2*n*t^2)",
        "inputs": {"t": t, "n": n},
        "bound": value,
        "proof_status": "PROVEN(Hoeffding)",
        "provenance": "szl-holdings/szl-formulas formula_atlas.v1.json",
    }


def certify_risk(errors: int, n: int, delta: float = 0.05) -> dict:
    """Certify a model's risk bound from a measured 0/1 evaluation sample.

    errors = number of failed probes; n = total probes; delta = confidence level.
    Returns the Hoeffding bound (distribution-free) and, when a KL divergence
    to a prior policy is available, the PAC-Bayes bound (tighter).
    """
    if not isinstance(errors, int) or isinstance(errors, bool) or errors < 0:
        raise ValueError("errors must be a non-negative int")
    if n < 8:
        raise ValueError("n must be >= 8 for a meaningful bound")
    if errors > n:
        raise ValueError("errors cannot exceed n")
    emp = errors / n
    # Hoeffding: with confidence 1-delta, true risk <= emp + t where
    # exp(-2*n*t^2) = delta  =>  t = sqrt(ln(1/delta) / (2n))
    t = math.sqrt(math.log(1.0 / delta) / (2.0 * n))
    hoeffding = hoeffding_tail(t, n)
    pac = pac_bayes_mcallester(emp, kl=0.0, n=n, delta=delta)
    return {
        "schema": "szl.underwriting.risk-bound/v1",
        "measured": {"errors": errors, "n": n, "empirical_risk": emp},
        "confidence": 1.0 - delta,
        "hoeffding_bound": emp + t,
        "hoeffding_detail": hoeffding,
        "pac_bayes_bound_kl0": pac["bound"],
        "pac_bayes_detail": pac,
        "interpretation": (
            f"With confidence {1.0 - delta:.0%}, the true failure rate is at most "
            f"{emp + t:.4f} (Hoeffding, distribution-free). The PAC-Bayes bound with "
            f"KL=0 (prior = posterior) is {pac['bound']:.4f}. Note: the PAC-Bayes "
            f"bound is monotonically increasing in KL, so KL=0 is its tightest "
            f"case; a measured KL>0 only loosens it. PAC-Bayes improves on "
            f"Hoeffding only when KL + ln(2*sqrt(n)/delta) < ln(1/delta), which "
            f"never holds at KL=0 for n >= 1; the reported KL=0 bound is "
            f"therefore looser than Hoeffding and is shown for reference only."
        ),
        "honesty": (
            "The bound certifies the arithmetic on the measured sample, not the "
            "truth of the inputs. The PAC-Bayes Lean obligation is open (SORRY), "
            "carried verbatim. This is one certificate axis; the Lambda-spine gate "
            "vetoes on any failed measured check."
        ),
        "truth_label": "MEASURED_STATISTICAL_BOUND",
    }


if __name__ == "__main__":
    import json
    import sys
    errors = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 48
    print(json.dumps(certify_risk(errors, n), indent=1))
