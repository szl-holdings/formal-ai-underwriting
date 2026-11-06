# Formal AI Underwriting

**The UL certification for AI: provably auditable models as a service.**

> We're the only company that can prove — with machine-checked math and cryptographic receipts — exactly what a model was trained on, what it will refuse to do, and when it expires. We're not competing with OpenAI. We're becoming the regulatory standard they'll have to comply with.

## What we certify

| Certification | What it proves | How |
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
4. **Expiry Guarantee** — theorem-backed performance degradation curve with automated refusal at expiry
5. **Reproducibility Package** — heartbeat logs, hyperparameters, dataset provenance per example

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
- **Inference (x402, per-call):** $0.02-$0.10 via Cloudflare monetization
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
- [x] x402 monetization live on Cloudflare (10 payment rules)
- [x] 17+ models trained with proof receipts
- [ ] First certification report template
- [ ] First pilot customer (pharma or legal)
- [ ] Published regulatory positioning paper

## License

Apache-2.0

---

Part of the [SZL Holdings](https://github.com/szl-holdings) governed estate.
**Control before action. Evidence after.**

Estate on Hugging Face: models, datasets and Spaces are published under the [SZLHOLDINGS](https://huggingface.co/SZLHOLDINGS) org.
