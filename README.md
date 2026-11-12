# Formal AI Underwriting

<!-- szl:header v1 -->
<!-- Native identity: szl-brand@4309f6fce89179331b0b3ed8c99494e76c5be256; Orbit v2 icon. -->
<p>
  <a href="https://github.com/szl-holdings">
    <img src="https://raw.githubusercontent.com/szl-holdings/szl-brand/4309f6fce89179331b0b3ed8c99494e76c5be256/kit/logos/orbit-v2/suite/szl-icon-32.svg" alt="SZL Holdings — Orbit v2" width="32" height="32" />
  </a>
</p>

**Control before action. Evidence after.**

[Product](https://a-11-oy.com) · [Proof](https://a11oy.net) · [GitHub organization](https://github.com/szl-holdings)
<!-- /szl:header -->

**Auditable AI models as a service: signed training-data receipts plus Lean-checked receipt formulas.** (No third-party certification is claimed.)

> We aim to make it checkable what a model was trained on (signed receipts), which refusal policy it was evaluated against (measured, with sample sizes), and when its policy expiry is set. Lean proofs cover the locked receipt formulas, not model behaviour.

## What this repository is

Formal AI Underwriting is SZL Holdings' model-certification offer. This repository holds its product
specification — the standard below, the [certification report template](templates/certification-report.md),
[pricing](docs/pricing.md), the [OpenAPI description](docs/openapi.yaml) of the x402-metered inference API and an
[ISO/IEC 42001 mapping](docs/iso42001-audit-package.md) — plus one executable, standard-library-only Python module,
[`certification/bounds.py`](certification/bounds.py), which computes the statistical risk bound in section 5 of
every report. The receipt chain, Lean proofs, training pipeline and inference service described below live in other
szl-holdings repositories and services; this repository does not implement or verify them (see
[Proof boundary](#proof-boundary)).

The optional [`payments.paycheck`](docs/paycheck.md) adapter adds a standard-library-only, fail-closed preflight for
x402 callers. It can read an unpaid `402 PAYMENT-REQUIRED` quote, checks the exact endpoint, amount, payout wallet
and network, and blocks signing unless PayCheck explicitly allows the payment. It does not sign or submit payments
and does not change certification evidence.

## What we certify

| Certification | What it covers | How |
|---|---|---|
| **Training Data Lineage** | Exactly which data trained the model, cryptographically linked | Khipu receipt-chain (append-only, hash-linked, offline-verifiable) |
| **Abstention Guarantee** | The model refuses to fabricate values outside its training distribution | Doctrine abstention (eval-driven, measured confabulation → counterweight → retrain → verify) |
| **Safety Properties** | Mathematical invariants hold (coherence decay, fixed-point convergence) | Lean 4 machine-checked theorems (locked-8 kernel, frozen at commit) |
| **Model Expiry** | When the model becomes unreliable and must be retrained | Lambda-v5 coherence decay theorem (Conjecture 1, advisory-only) |

## The certification report

Every certified model ships with:

1. **Khipu Training Receipt** — cryptographic hash-chain proving what data was used, when, and by which training run
2. **Lean Proof Certificate** — machine-checked theorems verifying safety invariants
3. **Doctrine Evaluation Receipt** — verbatim model outputs on abstention probes (no invented numbers, no fabricated citations)
4. **Expiry Guarantee** — advisory performance-degradation horizon (Conjecture 1, advisory-only; not a proven bound) with automated refusal at expiry
5. **Reproducibility Package** — heartbeat logs, hyperparameters, dataset provenance per example
6. **Statistical Risk Bound** — Hoeffding bound on the true failure rate from the measured probe sample, computed by `certification/bounds.py`

## Quick start: compute a certificate's risk bound

Needs Python 3.11 or newer and nothing else (no runtime dependencies):

```bash
git clone https://github.com/szl-holdings/formal-ai-underwriting
cd formal-ai-underwriting
python -m certification.bounds 3 48      # 3 failed probes out of 48; delta = 0.05
```

Output (excerpt, `...` marks omitted lines):

```text
{
 "schema": "szl.underwriting.risk-bound/v1",
 "measured": {
  "errors": 3,
  "n": 48,
  "empirical_risk": 0.0625
 },
 "confidence": 0.95,
 "hoeffding_bound": 0.23915091145020284,
 ...
 "pac_bayes_bound_kl0": 0.30455026939081364,
 ...
 "truth_label": "MEASURED_STATISTICAL_BOUND"
}
```

From Python:

```python
from certification.bounds import certify_risk

cert = certify_risk(errors=3, n=48, delta=0.05)
print(round(cert["hoeffding_bound"], 4))  # 0.2392
```

Invalid inputs (for example `delta=0`, a non-integer `n`, or more errors than probes) raise `ValueError`; no bound is
returned for them.

## Install and test

```bash
python -m pip install -e '.[test]'           # installs the `certification` package and pytest
python -m pytest                             # runs tests/test_bounds.py
python -m unittest discover -s tests -v      # same suite, standard library only, no install needed
```

The optional x402 payment preflight is documented in [`docs/paycheck.md`](docs/paycheck.md). It is available as the
`szl-paycheck-preflight` command after package installation.

CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) runs the suite on CPython 3.11–3.14 and checks that the
built wheel ships both executable packages and that its CLIs run from outside the checkout.

## Target markets

| Market | Regulatory Driver | Our Advantage |
|---|---|---|
| **Pharma/Clinical** | FDA requires training data lineage for AI-assisted drug safety | Only provider with cryptographic proof of training data |
| **Legal AI** | Courts demand verifiable citations; hallucinated case law = malpractice | Doctrine abstention: model refuses rather than fabricates |
| **Financial Modeling** | SEC/ESMA audits require model risk documentation | Lean proofs of distributional properties + expiry guarantees |
| **Insurance** | Underwriting models must be explainable and auditable | Full receipt chain from training to inference |

## Revenue model

- **Certification per deployment:** $50k-$500k
- **Annual audit retainer:** $20k-$100k
- **Inference (x402, per-call):** $0.02 per request on the chat, completions and responses paths the Cloudflare Monetization Gateway charges ([docs/pricing.md](docs/pricing.md))
- **Retraining (subscription):** $100k+/yr per model with expiry guarantees

## The moat

This stack requires:
- Lean 4 formal verification expertise (2+ years accumulated)
- Khipu receipt-chain infrastructure (already operational)
- Doctrine abstention training pipeline (proven through 2+ eval cycles)
- x402 monetization infrastructure (live on Cloudflare)

OpenAI can't retrofit provenance into GPT-4. Anthropic's Constitutional AI is prompting, not verification. NVIDIA sells GPUs, not AI auditing.

**This is a new category. We define the standard before regulators force it.**

## Status

- [x] Khipu receipt-chain operational
- [x] Lean 4 locked-8 kernel frozen
- [x] Doctrine abstention eval pipeline proven (2 full cycles)
- [x] x402 monetization on Cloudflare: 4 of 17 gateway rules enabled (a-11-oy.com: 4 of 15; a11oy.net: 0 of 2), per the fresh rules readback of 2026-11-11 at 16:40 UTC ([prices](docs/pricing.md))
- [x] 17+ models trained with proof receipts
- [x] First certification report template ([templates/certification-report.md](templates/certification-report.md))
- [ ] First pilot customer (pharma or legal)
- [ ] Published regulatory positioning paper

Except for the report template, these items describe systems outside this repository; they are owner-reported and
not checked by this repository's tests. As of 2026-11-06 the Hugging Face datasets that hold the eval and training
receipts (`SZLHOLDINGS/model-eval-receipts`, `SZLHOLDINGS/wave-logs`) are private, so third parties cannot yet inspect
them.

## Proof boundary

What this repository's code establishes, and what it does not:

- **Computed and tested here:** `certify_risk(errors, n, delta)` returns the one-sided Hoeffding bound
  `errors/n + sqrt(ln(1/delta) / (2n))` and, for reference, the McAllester/Maurer PAC-Bayes value at KL = 0, in IEEE-754
  floating point, and raises `ValueError` on invalid input. `tests/test_bounds.py` checks the closed form, the
  fail-closed behaviour, the documented CLI and, over a grid of `n`, `delta`, empirical risk and KL ≥ 0, that the
  PAC-Bayes value is never tighter than Hoeffding (which holds for every KL ≥ 0 because
  `ln(2·sqrt(n)/delta) > ln(1/delta)`).
- **Statistical assumption:** the bound is a statement about the true failure rate only if the `n` probes are i.i.d.
  draws from the distribution the certificate covers and the model was fixed before they were drawn. For a curated or
  adversarial probe set it summarises that set; it is not a guarantee about deployment behaviour.
- **Proof status, carried verbatim** from `formula_atlas.v1.json` in
  [szl-formulas](https://github.com/szl-holdings/szl-formulas): Hoeffding `PROVEN(MomentSubGaussian)` — the Lean
  theorem `hoeffding_mgf_tail_bound` in [lutar-lean](https://github.com/szl-holdings/lutar-lean)
  (`Lutar/PACBayes.lean`) is conditional on the axiom `MomentSubGaussian`; PAC-Bayes `SORRY(PACBayes)` — the Lean
  obligation is open.
- **Not proven by this repository:** training-data lineage, abstention behaviour, safety invariants and expiry. A
  hash-linked receipt chain shows a recorded lineage was not altered after the fact; it does not by itself show the
  record is complete. Abstention is measured on finite probe sets, not proven. The Lean theorems cited in the report
  are about the estate's mathematical objects, not about a trained model's weights or outputs. The expiry horizon is
  advisory (Conjecture 1).
- **Not tested here:** the inference API at `api.a-11-oy.com`, its prices and the Cloudflare payment rules are operated
  outside this repository; nothing in this repository exercises them.

## Links

- Source: [github.com/szl-holdings/formal-ai-underwriting](https://github.com/szl-holdings/formal-ai-underwriting)
- Formula source: [szl-formulas](https://github.com/szl-holdings/szl-formulas) · Lean proofs: [lutar-lean](https://github.com/szl-holdings/lutar-lean)
- Models offered through the API ([docs/openapi.yaml](docs/openapi.yaml)) on Hugging Face:
  [SZL-Nemotron-Mini-4B-Estate-v1](https://huggingface.co/SZLHOLDINGS/SZL-Nemotron-Mini-4B-Estate-v1) ·
  [SZL-Khipu-1.5B-estate-sft-v1](https://huggingface.co/SZLHOLDINGS/SZL-Khipu-1.5B-estate-sft-v1) ·
  [szl-receiptagent-qwen35-0.8b-dpo-v2](https://huggingface.co/SZLHOLDINGS/szl-receiptagent-qwen35-0.8b-dpo-v2)
- Product site: [a-11-oy.com](https://a-11-oy.com)

## License

Apache-2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE).

---

Part of the [SZL Holdings](https://github.com/szl-holdings) governed estate.
**Control before action. Evidence after.**

Estate on Hugging Face: models, datasets and Spaces are published under the [SZLHOLDINGS](https://huggingface.co/SZLHOLDINGS) org.
