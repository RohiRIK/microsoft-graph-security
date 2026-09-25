---
type: Workflow
title: "Access-Denied Triage (Nested Group Conflicts)"
description: "Trace why a user is blocked from an app by recursively resolving group inheritance, then propose a gated remediation. Executable version of operational flow 02."
tags: [security-ops, conditional-access, groups, entra]
timestamp: 2026-07-03T00:00:00Z
---

# Access-Denied Triage

Source flow: `docs/operational-flows/02-mfa-deficiencies-risk-triage.md`

## Steps

1. **Resolve the user and the app.**
   - `entra.search_users` → `entra.get_user`.
   - `entra.search_applications` → `entra.get_application`; `entra.get_service_principal` for the enterprise app (assignment requirements, assigned groups).
2. **Resolve effective membership — direct vs inherited.**
   - `entra.list_user_groups` (direct) and `entra.list_user_transitive_member_of` (effective).
   - Anything in the transitive set but not the direct set is inherited — for each, walk the chain with `entra.list_group_transitive_members` / `entra.get_group` until the path from user to blocking group is explicit.
3. **Check the failure evidence.** `entra.list_sign_ins` for the user filtered to the app and recent window — the sign-in record carries the failure reason and applied policy names.
4. **Pinpoint and report.** State the exact inheritance path (e.g. user → "Dept-X" → nested "Contractors" → blocked) and the sign-in failure evidence.
5. **Remediate (gated).** Options, in order of preference:
   - Add user to the app's exception/access group: `entra.add_group_member` (write_standard, two-phase confirm).
   - Remove user from the toxic inherited group: `entra.remove_group_member` (write_destructive, two-phase confirm) — only with group-owner signoff (`entra.list_group_owners`).
6. **Verify.** Re-run `entra.list_user_transitive_member_of`; ask the user to retry; check the new `entra.list_sign_ins` entry succeeds.

## Flag rules in play

- **MFA_WEAK** — if the sign-in failures are MFA-related and the user is privileged (`entra.list_role_assignments`), escalate rather than white-list.

## Capability boundaries

- **No Conditional Access policy read tools.** The CA policy itself cannot be listed or diffed; policy names come only from sign-in log evidence (step 3). Deep CA analysis is a manual portal step.
- **Sign-in/audit tools are rate-limited hard (10/min)** — always bound with date filters.
