---
name: break-glass-account-audit
description: Verify that a tenant's break-glass/emergency-access accounts are excluded from every enabled Conditional Access policy, and execute confirm-gated remediation to patch missing exclusions. USE WHEN before promoting any CA policy to enabled, during a periodic tenant health check, asked 'are our break-glass accounts actually safe', or 'patch break-glass exclusions into our CA policies'. NOT FOR creating CA policies from scratch (use conditional-access-provisioning).
metadata:
  category: workflow
  effort: medium
  tags: entra, conditional-access, break-glass, emergency-access, audit, remediation
---

# break-glass-account-audit

`update_conditional_access_policy_state`'s promotion guard (in `conditional-access-provisioning`)
only proves a policy excludes *some* user or group — it cannot verify those exclusions point
at real, monitored, properly-protected emergency-access accounts. This skill closes that gap
with an independent verification check, and provides **automated, confirm-gated remediation**
via `entra.patch_breakglass_exclusions` when policies are found lacking proper emergency access exclusions.

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **VerifyBreakGlassCoverage** | "check break-glass accounts", "are we protected from CA lockout", "emergency access audit" | `Workflows/VerifyBreakGlassCoverage.md` |
| **PatchBreakGlassExclusions** | "patch break-glass accounts into CA", "remediate break-glass exclusions", "add emergency accounts to policies" | `Workflows/PatchBreakGlassExclusions.md` |

## Ground Rules

1. **A break-glass account must be excluded from every enabled CA policy**, not just the one about to be promoted — a gap in even one enabled policy defeats the purpose during an outage affecting that specific control.
2. **Break-glass accounts should NOT have everyday-use sign-in activity** — frequent sign-ins from a "break glass" account is itself a finding (it suggests either misuse or that it's not really break-glass).
3. **Authentication method matters more than exclusion.** An excluded account secured only by SMS/password is still a lockout risk if the phishing/compromise vector is credential-based, not CA-based.

## Gotchas

- There's no Graph attribute that flags an account "is break-glass" — identify candidates by tenant convention (naming pattern, a dedicated admin-unit or group) agreed with the operator up front; don't guess from `get_user` alone.
- `list_conditional_access_policies` includes disabled and report-only policies too — filter to `state: enabled` before checking exclusion coverage; a gap in a disabled policy isn't currently exploitable.

## Examples

**Example 1: Pre-promotion gate**
```
User: "About to promote the new MFA policy — are break-glass accounts covered?"
→ VerifyBreakGlassCoverage → list_conditional_access_policies (state=enabled) → checks each policy's excludeUsers/excludeGroups against the known break-glass account list
→ Reports coverage gaps, if any, before promotion proceeds
```
