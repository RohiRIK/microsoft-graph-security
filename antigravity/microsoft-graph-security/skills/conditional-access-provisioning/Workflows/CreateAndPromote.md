---
type: Workflow
title: "Create and Promote a Conditional Access Policy"
description: "Two-phase rollout: create in a non-enforcing state, review impact, then promote to enabled."
tags: [entra, conditional-access]
timestamp: 2026-07-31T00:00:00Z
---

# Create and Promote

## Steps

1. **Gather requirements**: display name, target users/groups (`include_users`/`include_groups`, `exclude_users`/`exclude_groups`), target apps (`include_applications`), client app types, grant controls (`built_in_controls` — e.g. `mfa`, `compliantDevice`, `block`), grant operator (`AND`/`OR`).
2. **Create** — `entra.create_conditional_access_policy` without `confirm` first; show the preview (display name + resolved state) to the operator.
   - Default `state` if unspecified: `enabledForReportingButNotEnforced` (report-only, not disabled) — say this explicitly.
3. Operator approves → re-call with `confirm: true`. Policy now exists, non-enforcing.
4. **Review impact.** Ask the operator to check the policy's report-only sign-in logs in the Entra portal (no tool surfaces this directly) for a representative window before promoting.
5. **Check break-glass coverage** — run `break-glass-account-audit` if it hasn't been run recently for this tenant. Do not skip this before promoting to `enabled`.
6. **Promote** — `entra.update_conditional_access_policy_state` with `state: enabled`, no `confirm` first.
   - If it refuses (`no users or groups excluded`), stop and have the operator add real break-glass exclusions to the policy in the portal or via a follow-up `create`/`update` cycle — do not work around the refusal by pointing exclusions at an arbitrary group just to satisfy the check.
7. Operator approves → re-call with `confirm: true`. Policy is now live.

## Flag rules in play

- Treat a promotion request with no prior report-only review window as a red flag — recommend at least a short observation period before promoting, even though no tool enforces this.

## Capability boundaries

- No tool reads report-only sign-in impact directly (Entra's report-only evaluation logs aren't exposed via a dedicated Graph list tool here) — that review step is manual, in the portal.
