# Model Certification Report

## Certificate ID: [UUID]
## Model: [model_id]
## Certification Date: [date]
## Certifying Authority: SZL Holdings LLC

---

## 1. Training Data Lineage

**Khipu Receipt Chain:**
- Training run ID: [run_id]
- Heartbeat log: [wave_logs_link]
- Datasets used (with per-example provenance):
  - [dataset_1]: [num_examples] examples, [provenance]
  - [dataset_2]: [num_examples] examples, [provenance]
- Training data hash-chain head: [chain_hash]
- Verification: Any third party can verify offline using [verify_command]

**Data Rights:**
- All training data is [license_type] licensed
- No personally identifiable information used: [confirmed_by]
- Contamination check: [method, result]

## 2. Safety Invariants

**Lean 4 Machine-Checked Theorems:**
- Kernel: locked-8 (F1, F4, F7, F11, F12, F18, F19, F22) at commit c7c0ba17
- Coherence decay theorem: [Wave24] verified
- Kleene LFP theorem: [Wave25/26] verified
- All proofs: sorry-free, Lean-core axioms only

**Doctrine Abstention Evaluation:**
- Eval receipt: [eval_receipt_link]
- Abstention probes: [num_probes]
- Fabrication incidents: [num_incidents] (must be 0 for certification)
- Truth-label compliance: [rate]%

## 3. Model Expiry Guarantee

**Lambda-v5 Coherence Decay (Conjecture 1, advisory):**
- Expected coherence decay horizon: [months]
- Out-of-distribution threshold: [description]
- Automated refusal trigger: [condition]
- Retraining recommendation: [months] months

## 4. Reproducibility

**Training Configuration:**
- Hardware: [gpu_model]
- Method: [method] (r=[r], lr=[lr], epochs=[epochs], seqlen=[seqlen])
- Training steps: [steps]
- Final loss: [loss]
- Train receipt: [receipt_link]

**Verification:**
- Proof banner: [banner_link]
- Model card: [card_link]
- HF repository: [hf_link]

## 5. Certification Statement

This model has been certified by SZL Holdings LLC as meeting the Formal AI Underwriting standard:
- [ ] Training data lineage cryptographically verified
- [ ] Safety invariants machine-checked (Lean 4)
- [ ] Doctrine abstention verified (zero fabrication on probes)
- [ ] Expiry guarantee defined and automated
- [ ] Reproducibility package complete

**Certified by:** [name]
**Date:** [date]
**Certificate hash:** [sha256]
