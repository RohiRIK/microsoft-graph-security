---
type: Workflow
title: "Legal Hold Coverage Check"
description: "Verify a specific custodian is actually on hold for an active case, not just assumed to be."
tags: [purview, legal-hold, hold-gap]
timestamp: 2026-07-31T00:00:00Z
---

# Legal Hold Coverage Check

## Steps

1. Resolve the case: `purview.get_ediscovery_case` (by ID) or `purview.list_ediscovery_cases` (by name/status filter).
2. Refuse to proceed past this point if the case is closed and the request implies an active hold — surface that contradiction immediately instead of checking custodians for a closed case.
3. `purview.list_ediscovery_custodians` — match by `email` (case-insensitive) against the UPN in the request.
4. If the case covers shared mailboxes or sites instead of a named user, check `purview.list_ediscovery_noncustodial_data_sources` instead.
5. Report: held / not held / held-but-released. If held-but-released while the case is still active, flag **HOLD_GAP**.

## Flag rules in play

- **HOLD_GAP** — custodian hold not applied while the case is active, or released before the case closed.

## Capability boundaries

- Read-only. Applying or releasing a hold is a manual eDiscovery (Premium) portal action — this workflow's job ends at the finding.
