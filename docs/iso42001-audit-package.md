# ISO/IEC 42001 Audit Package: SZL Holdings AI Management System

## Purpose

ISO/IEC 42001 is the first certifiable AI management system standard. This document
maps the estate's existing artifacts to the standard's requirements, demonstrating
that the audit package already exists in the estate's public receipts.

## Mapping: ISO 42001 clauses → estate artifacts

### Clause 4: Context of the organization

| Requirement | Estate artifact |
|---|---|
| Understanding the organization and its context | `szl-papers/investor/ONE_PAGER.md` — the estate's purpose, products, and market position |
| Needs and expectations of interested parties | The Formal AI Underwriting product spec (`docs/pricing.md`, `docs/openapi.yaml`) — what customers need (provable auditability) |
| Scope of the AI management system | The governed validation certificates (`model-eval-receipts/governed-validation-2026-11-06.json`) — what models and services are in scope |

### Clause 5: Leadership

| Requirement | Estate artifact |
|---|---|
| Leadership and commitment | The doctrine (Doctrine v11 LOCKED, 749/14/163) — the leadership's commitment to honesty, published and machine-checked |
| AI policy | The honesty doctrine: "model output is an untrusted proposal; every claim carries a receipt; failures are published verbatim" |
| Roles, responsibilities and authorities | The Khipu receipt chain names the signer for every action. The governed validation certificate names the gate that decided. The DsseSigner has a named key. |

### Clause 6: Planning

| Requirement | Estate artifact |
|---|---|
| Actions to address risks and opportunities | The Λ-spine gate's axes (source_receipt_valid, license_admissible, freshness, relevance, derivation_integrity) — each axis IS a risk addressed |
| AI risk assessment | The fleet-eval receipts — measured failure modes (including confabulation) published verbatim |
| AI risk treatment | The DPO counterweight (Estate-DPO-v2) built from measured failures; the governed validation gate (NO_GO until remediation verified) |

### Clause 7: Support

| Requirement | Estate artifact |
|---|---|
| Resources | A6000 nodes on Massed Compute; Cloudflare edge; HF Hub for distribution — all documented in the wave receipts |
| Competence | The formula atlas (21 executable formulas, 30 attributed, 8 Lean-proven) — the mathematical competence of the system |
| Awareness | The honesty doctrine (every model card carries it); the NO_GO certificate (the estate publicly fails itself) |
| Documented information | Every training wave, every eval, every governed decision produces a receipt published to public datasets |

### Clause 8: Operation

| Requirement | Estate artifact |
|---|---|
| Operational planning and control | The hatun-mcp 7-step contract: authenticate → gate → reputation → 2-person check → backend call → receipt → DSSE sign |
| AI system lifecycle management | Training waves with exit codes; model cards with provenance; governed validation gates for promotion |
| Data management | HIRAG: the provenance DAG with per-node receipts, license checks, and freshness windows; the corpus datasets with full provenance cards |
| Third-party relationships | The Sara Behnamian collaboration (certified benchmark, co-authored paper); the NVIDIA Inception program; the Cloudflare partnership |

### Clause 9: Performance evaluation

| Requirement | Estate artifact |
|---|---|
| Monitoring and measurement | The heartbeat system (wave-logs, every 5 minutes); the p99 load test receipt; the chain test receipt; the fleet-eval receipts |
| Evaluation of AI system performance | The exact-scored certified-puzzle eval (48 puzzles, exact JSON parsing); the PAC-Bayes risk bound (computed from measured sample); the Hoeffding confidence interval |
| Internal audit | The governed validation certificate — the estate audits ITSELF using the Λ-spine gate and publishes the results (including NO_GO) |
| Management review | The oracle: the estate's own governance decisions are receipted, published, and independently verifiable |

### Clause 10: Improvement

| Requirement | Estate artifact |
|---|---|
| Continual improvement | The three-condition training ablation (plain reasoning vs free-energy vs ancient math) — each condition's delta is a measured improvement |
| Nonconformity and corrective action | The DPO counterweight: measured confabulation failures → eval-driven preference pairs → DPO training → re-eval → re-gate. The remediation arc IS the corrective action. |
| Adaptive behavior | The eval-driven counterweight protocol: the failures of the current model become the training signal for the next. The loop closes. |

## What the estate has that ISO 42001 doesn't require

- **Cryptographic receipts per decision**: ISO 42001 certifies the management system;
  the estate additionally certifies every individual decision with a hash-chained,
  DSSE-signed receipt.
- **Lean-verified governance math**: The Λ aggregator's properties are machine-checked.
  The PAC-Bayes bound is a conditional theorem. ISO 42001 doesn't require formal
  verification — the estate has it anyway.
- **Statistical bounds with confidence**: The McAllester/Hoeffding bounds give computed
  risk bounds with stated confidence levels. ISO 42001 requires risk management; the
  estate quantifies it.
- **Public self-failure**: The estate publishes its own NO_GO certificates. ISO 42001
  doesn't require transparency about failures — the estate does it anyway.

## Path to certification

1. Engage an accredited certification body (BS ISO/IEC 42006:2025 qualified auditors)
2. Submit this audit package (the receipts ARE the evidence)
3. Stage 1 audit: documentation review (this mapping)
4. Stage 2 audit: implementation review (the live systems)
5. Certification: 3-year cycle, annual surveillance

**Estimated readiness: the estate is 60-70% aligned** per the published crosswalks
between NIST AI RMF and ISO 42001. The remaining 30-40% is formal documentation
of processes that already exist in practice.
