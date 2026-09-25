---
type: Workflow
title: "Verify Break-Glass Account Coverage"
description: "Cross-check every enabled CA policy's exclusions against the tenant's known emergency-access accounts."
tags: [entra, conditional-access, break-glass]
timestamp: 2026-07-31T00:00:00Z
---

# Verify Break-Glass Coverage

## Steps

1. **Identify candidates.** Ask the operator which accounts/groups are the tenant's designated break-glass accounts if not already known — don't infer this from naming conventions alone without confirmation.
2. `entra.list_conditional_access_policies` — filter to `state: enabled` only (disabled/report-only policies aren't currently enforcing, lower priority).
3. For each enabled policy, `entra.get_conditional_access_policy` (or use the list response if it already includes `conditions.users`) — check `excludeUsers`/`excludeGroups` against the candidate list.
4. **Flag any enabled policy where none of the known break-glass accounts/groups appear in its exclusions.**
5. `entra.list_user_authentication_methods` for each break-glass account — flag any relying on SMS/voice/password-only rather than a phishing-resistant method (FIDO2, certificate-based).
6. `entra.list_sign_ins` for each break-glass account, recent window — flag unexpected regular-use activity (should be near-zero outside genuine emergencies/scheduled tests).
7. Report: per-policy coverage table, auth-method findings, sign-in activity findings.

## Flag rules in play

- **MFA_WEAK** — break-glass account secured by a phishable method.
- Coverage gap on any enabled policy is a hard blocker for any pending CA promotion (see `conditional-access-provisioning`) — say so explicitly, don't just log it as an FYI.

## Capability boundaries

- No Graph attribute marks an account as break-glass; this workflow depends on the operator naming the correct accounts up front. A wrong or incomplete candidate list produces false "all clear" results — state this limitation in the report.
