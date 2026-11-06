# ISO/IEC 42001 Audit Package: SZL Holdings AI Management System

## Purpose

ISO/IEC 42001 is the first certifiable AI management system standard. This document
maps the estate's existing artifacts to the standard's requirements, showing where
evidence for each clause already exists in the estate's receipts. It is a mapping,
not an audit, and some of the receipts it cites are not public yet (see below).

## Status and evidence availability (read first)

- **Not certified, and no clause family implemented yet.** The estate's internal gap
  analysis, [`platform/docs/compliance/ISO_42001_GAP.md`](https://github.com/szl-holdings/platform/blob/main/docs/compliance/ISO_42001_GAP.md)
  (assessed 2026-07-25), rates Clause 4 **OPEN** and Clauses 5–10 **PARTIAL**, marks no
  clause family IMPLEMENTED, and records that no AIMS scope has been approved. Read this
  mapping together with that analysis.
- **Evidence availability, checked 2026-11-06** (Hugging Face Hub API without credentials;
  GitHub repository visibility):

| Evidence cited below | Location | Public? |
|---|---|---|
| Governed validation certificates (`governed-validation-2026-11-06.json`, v2, v3, incl. the NO_GO), fleet-eval, doctrine-abstention eval, load-test and chain-test receipts | HF dataset `SZLHOLDINGS/model-eval-receipts` | **No** — private (HTTP 401) |
| Heartbeat / wave logs | HF dataset `SZLHOLDINGS/wave-logs` | **No** — private (HTTP 401) |
| Training corpus and DPO counterweight pairs (`estate-knowledge-corpus-v1`, `doctrine-abstention-dpo-v2`) | HF datasets under `SZLHOLDINGS` | **No** — private (HTTP 401) |
| Estate-trained models and their cards (e.g. `SZL-Nemotron-Mini-4B-Estate-v1`) | HF models under `SZLHOLDINGS` | Yes |
| Investor one-pager (`investor/ONE_PAGER.md`) | GitHub `szl-holdings/szl-papers` | Yes |
| Formula atlas (`formula_atlas.v1.json`) | GitHub `szl-holdings/szl-formulas` | Yes |
| Lean proofs | GitHub `szl-holdings/lutar-lean` | Yes |

  Until the private datasets are published or shared with the certification body, the
  statements below that call these receipts public describe intent, not current state.

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
| Awareness | The honesty doctrine (every model card carries it); the NO_GO certificate (the estate fails itself on the record; the certificate is in the private `model-eval-receipts` dataset) |
| Documented information | Every training wave, every eval, every governed decision produces a receipt published to Hugging Face datasets (several private as of 2026-11-06; see the table above) |

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
- **Self-failure on the record**: The estate records its own NO_GO certificates. ISO 42001
  doesn't require transparency about failures — the estate does it anyway (the certificates
  become public once `SZLHOLDINGS/model-eval-receipts` is published; it is private as of 2026-11-06).

## Path to certification

0. Close the gaps in the internal gap analysis first. In its words, certification is targeted
   "only after the organization has approved an AIMS scope, operated the system long enough to
   produce evidence, completed an internal audit and management review, closed material
   nonconformities, and authorized an external certification engagement."
1. Engage an accredited certification body (BS ISO/IEC 42006:2025 qualified auditors)
2. Submit this audit package (the receipts ARE the evidence)
3. Stage 1 audit: documentation review (this mapping)
4. Stage 2 audit: implementation review (the live systems)
5. Certification: 3-year cycle, annual surveillance

**Estimated readiness: 60-70% (unaudited self-estimate).** The published crosswalks
between NIST AI RMF and ISO 42001 map clauses between the two frameworks; they do not
measure this estate, and no scored assessment behind the figure is published. The internal
gap analysis linked above marks no clause family as implemented and lists open processes,
not only documentation (an approved AIMS scope, AI impact assessments, an internal audit
programme, management reviews).
