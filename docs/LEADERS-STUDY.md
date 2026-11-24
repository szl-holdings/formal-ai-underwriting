<!-- PROPOSE-ONLY / DO-NOT-MERGE. Study document only. No code, config, or workflow change is proposed by this file. -->
# LEADERS-STUDY -- formal-ai-underwriting (tranche 6, 2026-11-24)

> **PROPOSE-ONLY / DO-NOT-MERGE.** Per-repo-domain public-surface study card from the round-2 leader pack.
> Nothing here is approved for implementation. Merge requires a separate governing review plus a fresh owner GO naming repo, PR, and pin.

## 0. Scope gate

Study-only. This PR adds exactly one documentation file (this file). No code, no spec change, no pricing change, no certification claims added or upgraded. All absorb candidates are UNAPPROVED.

## 1. Current state (measured evidence, 2026-11-24 qualification)

- Repo: szl-holdings/formal-ai-underwriting, main tip at qualification 964b215fbad6ba7a543e63f1713f28969bea92f1, 49 files, zero open PRs at scan time.
- Contents measured: product specification, certification report template, docs/pricing.md, OpenAPI description of the x402-metered inference API, docs/iso42001-audit-package.md, and certification/bounds.py (stdlib-only statistical risk bound).
- Honesty boundaries in README: no third-party certification is claimed; Lean proofs cover the LOCKED RECEIPT FORMULAS, not model behaviour; receipt chain/pipeline/service live in other repos; docs/paycheck.md = fail-closed 402 preflight adapter only.
- Certification table: Training Data Lineage (Khipu receipt-chain), Abstention Guarantee (eval-driven, measured with sample sizes), policy expiry.

## 2. Field leaders (public-surface study, round-2 leader pack)

| # | Leader | Public source | Leads at |
|---|---|---|---|
| L1 | NIST AI RMF 1.0 + Generative AI Profile (NIST AI 600-1) | nist.gov AI Risk Management Framework pages | The public risk-management vocabulary auditors expect; mapping posture |
| L2 | ISO/IEC 42001:2023 management-system certification programs | iso.org 42001; public certification-body audit programs (**provider programs UNVERIFIED specifics**) | Third-party accredited AI-management certification (the thing this repo explicitly does NOT claim) |
| L3 | Axiom-style verified-math publishing (Weil Conjectures formalized) | axiommath.ai research pages (**AxiomProver depth UNVERIFIED, watch**) | Verified discoveries + published proof certificates |
| L4 | x402 agentic-payments standard adoption | chainalysis.com x402 adoption study; coindesk Visa/Mastercard/Ripple coverage | Standardized 402 payment-for-inference surface (paycheck adapter's home turf) |

## 3. Honest gaps (this repo vs the leaders)

- Gap A: an ISO/IEC 42001 mapping exists but no public NIST AI RMF mapping doc (L1 is the other half of the posture leaders expect).
- Gap B: certification evidence is self-issued; leaders L2 run accredited programs. README is honest about this -- the gap is posture, not honesty.
- Gap C: bounds.py computes report risk bounds but publishes no signed test-vector receipts (seeds, sizes, versions) that third parties can replay.
- Gap D: Lean-verified formulas have no published proof-certificate artifacts (L3's leader posture).

## 4. Absorb candidates A1-A4 (ALL UNAPPROVED)

- A1: Add a NIST AI RMF mapping document beside the ISO 42001 mapping. Applicability test: mapping cites public framework sections; zero new certification claims; fail-closed wording preserved.
- A2: Publish bounds.py test-vector receipts (inputs, seeds, sample sizes, library versions, sha). Applicability test: a third party can rerun bounds and reproduce the bound offline.
- A3: Proof-certificate export path for the locked Lean receipt formulas (L3 pattern). Applicability test: certificate artifacts verifiable in the estate lean toolchain; no unproven formula listed.
- A4: Bind x402-metered inference receipts to certification-report fields (L4 alignment). Applicability test: every metered call's receipt references the report + policy expiry it was evaluated against.

## 5. Open questions A5-A6 (governing gates)

- A5 (owner-gated): will the estate EVER seek accredited third-party certification, or is self-issued + verifiable evidence the permanent posture? Determines whether Gap B is a roadmap item or a stated non-goal.
- A6 (Kimi lap): how do paycheck preflight receipts and certification report fields stay in lockstep across report revisions (version skew between adapter and report)?

## 6. Non-goals

No implementation in this PR. No accredited-certification claim, ever, without an owner GO. No model-behaviour proof claims (Lean covers locked receipt formulas only). No merge without governing review + fresh owner GO naming repo, PR, and pin.

## 7. Markers and receipts

LEADERS_STUDY_TRANCH6_CARD_3_OF_6 | PROPOSE_ONLY_DNM | qualification tip 964b215f | erf scan C:/SZL/edge-debug/sp9_census.txt | qualification receipt ft_h4_t6qual.json (2026-11-24T13:46:23Z) | leader pack round2-leader-pack.md.
