# Scoring Harness — Vidal-Gadea / SZL collaboration (protocol-pending)

An evaluation harness for a multi-arm scoring study. Built to the specification
agreed in the collaboration correspondence (A. Vidal-Gadea, 2026-11-06):

  - **Arm declarations in code** — each arm declared as a versioned artifact
  - **Case loading format** — opaque case identifiers only; no ruling text, no
    agent output, no file names, no project-revealing counts
  - **Scoring interface** — the rubric plugs in when the draft protocol lands
    (~the 12th); symmetric scoring of unsupported inference vs missed constraints
  - **Analysis scripts** — operate only on the exported results table
  - **Export gate** — every artifact that leaves a site passes the same gate
  - **Hash pinning** — the harness is reviewed and pinned by hash before it runs

## Status (honest)
PROTOCOL-PENDING: the scoring rubric, the four arms, and the exportable fields
are specified in the draft protocol that arrives ~2026-11-12. Everything here
is the protocol-independent scaffolding; nothing in this repository claims
biological validity, and passing synthetic fixtures establishes method
behavior only — never biological validity (reciprocal clause, agreed).

## Licensing
No fixture is imported before its license is established (the AGPL/GPL lesson).
Each fixture carries a provenance record: source, license, source revision,
transformation history.
