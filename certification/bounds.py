#!/usr/bin/env python3
"""certification.bounds — statistical risk bounds for model certificates (formal-ai-underwriting).

Adapted from szl-holdings/szl-formulas (torch-ext/szl_formulas/_formulas.py;
proof statuses carried verbatim from formula_atlas.v1.json):
  * pac_bayes_mcallester — PROOF-STATUS: SORRY(PACBayes)
  * hoeffding_tail       — PROOF-STATUS: PROVEN(MomentSubGaussian)

hoeffding_tail here is the one-sided bound exp(-2*n*t^2); the atlas function
is the two-sided min(1, 2*exp(-2*n*t^2)). Its Lean counterpart is
szl-holdings/lutar-lean `hoeffding_mgf_tail_bound` (Lutar/PACBayes.lean), which
proves the one-sided tail conditional on the retained axiom `MomentSubGaussian`.

These are the mathematical backbone of the certification product: a model
certificate that carries a computed generalization bound from its measured
evaluation sample, with the formula provenance attached.

Honesty contract:
  * The bound is computed from caller-supplied measured inputs; it certifies
    the arithmetic, not the truth of the inputs.
  * As a statement about the true failure rate, the bound assumes the n probes
    are i.i.d. draws from the distribution the certificate speaks about and
    that the model was fixed before they were drawn (not tuned or selected on
    them). For a curated or adversarial probe set it summarises that set only.
  * A SORRY proof-status is carried verbatim: the Lean obligation is open.
    PROVEN(MomentSubGaussian) is conditional on that named Lean axiom.
  * Invalid inputs raise ValueError; nothing is clamped and no NaN bound is
    returned.
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

    One-sided Hoeffding bound (Hoeffding 1963, Thm 2) for n i.i.d. losses in
    [0,1]. The mirror tail P(E[X] - mean >= t) has the same bound; that is the
    tail certify_risk relies on ("true risk <= empirical risk + t").
    PROOF-STATUS: PROVEN(MomentSubGaussian) — carried verbatim from the source
    atlas; the Lean proof is conditional on the axiom MomentSubGaussian.
    """
    if not _real(t) or math.isnan(t) or t < 0:
        raise ValueError("t must be a non-negative real (NaN is not a number)")
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        raise ValueError("n must be a positive int")
    value = math.exp(-2.0 * n * t * t)
    return {
        "formula": "P(mean - E[X] >= t) <= exp(-2*n*t^2)",
        "inputs": {"t": t, "n": n},
        "bound": value,
        "proof_status": "PROVEN(MomentSubGaussian)",
        "provenance": "szl-holdings/szl-formulas formula_atlas.v1.json",
    }


def certify_risk(errors: int, n: int, delta: float = 0.05) -> dict:
    """Certify a model's risk bound from a measured 0/1 evaluation sample.

    errors = number of failed probes; n = total probes; delta = 1 - confidence.
    Returns the one-sided Hoeffding bound (distribution-free) and, for
    reference, the PAC-Bayes bound at KL=0. The PAC-Bayes bound is monotone
    increasing in KL and, on the same empirical risk, never tighter than the
    Hoeffding bound for any KL >= 0 (ln(2*sqrt(n)/delta) > ln(1/delta)).
    Raises ValueError on invalid inputs instead of returning a bound.
    """
    if not isinstance(errors, int) or isinstance(errors, bool) or errors < 0:
        raise ValueError("errors must be a non-negative int")
    if not isinstance(n, int) or isinstance(n, bool):
        raise ValueError("n must be an int (sample size)")
    if not _real(delta) or not (0.0 < delta < 1.0):
        raise ValueError("delta must be a real number in (0,1)")
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
