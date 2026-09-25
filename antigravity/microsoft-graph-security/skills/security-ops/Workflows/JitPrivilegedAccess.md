---
type: Workflow
title: "JIT Privileged Access (ChatOps)"
description: "Grant time-boxed privileged access tied to a ticket, then audit exactly what happened during the elevation window. Executable version of operational flow 01."
tags: [security-ops, jit, pim, privileged-access, entra]
timestamp: 2026-07-03T00:00:00Z
---

# JIT Privileged Access

Source flow: `docs/operational-flows/01-high-privilege-access-review.md`

## Steps

1. **Verify the requester.**
   - `entra.search_users` (name) → `entra.get_user` (resolve UPN + `accountEnabled`).
   - `entra.list_role_assignments` filtered to the user — refuse if they already hold the requested role.
   - `entra.list_sign_ins` for the user, last 24h — abort and flag RISKY_SIGNIN if any high-risk sign-in.
2. **Verify the ticket (manual gate).** No ITSM tool exists in this stack. Ask the operator to paste the ticket ID and confirm it is active and assigned to the requester. Record the ticket ID in the summary.
3. **Grant via role-assignable group** — `entra.add_group_member` (write_standard, two-phase: preview → operator approves → `confirm: true`). Target group must be the pre-built role-assignable group for the requested role; find it with `entra.search_groups` + `entra.list_group_owners`.
4. **Record the window.** Note grant time and agreed duration (default 2h) in the response. Schedule or ask the operator to trigger the revocation at expiry.
5. **Revoke at expiry** — `entra.remove_group_member` (write_destructive, two-phase confirm).
6. **Audit the window.**
   - `entra.list_directory_audits` bounded to the elevation window, filtered to the user.
   - `entra.list_sign_ins` for the same window.
   - Summarize: what was touched, from where, any MFA_WEAK or RISKY_SIGNIN evidence. Post the summary to the ticket (operator action).

## Flag rules in play

- **RISKY_SIGNIN** — high-risk sign-in during or before the window → recommend immediate `entra.revoke_sign_in_sessions`.
- **PRIV_RISK** — if the requester's device is noncompliant (`intune.search_managed_devices` by UPN → `complianceState`), surface before granting.

## Capability boundaries

- **No native PIM tools.** True PIM eligible-assignment activation is not available; this workflow approximates JIT via role-assignable group membership. Time-boxing is procedural (step 5), not enforced by the platform.
- **No ITSM integration.** Ticket verification is a manual operator gate.
