---
name: conditional-access-provisioning
description: Create and promote Conditional Access policies through entra_id_mcp's write_critical tools, structured so a new policy can never be created already-enforced. USE WHEN standing up a new CA policy, promoting a report-only policy to enforced, or asked to 'lock down' sign-in for an app/group. NOT FOR diagnosing why an existing policy is blocking someone (use security-ops's AccessDeniedTriage) or auditing break-glass exclusion coverage across existing policies (use break-glass-account-audit).
metadata:
  category: workflow
  effort: medium
  tags: entra, conditional-access, provisioning, write-critical
---

# conditional-access-provisioning

Two `entra.*` tools, both `write_critical`, both confirm-gated. The safety guarantee is
structural, not procedural: `create_conditional_access_policy`'s `state` field is a Zod enum
of exactly `['disabled', 'enabledForReportingButNotEnforced']` — there is no argument
combination that creates a live, enforcing policy. The only path to `enabled` is
`update_conditional_access_policy_state`, which refuses if the policy excludes zero users
and zero groups — the single most common real-world CA lockout cause.

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **CreateAndPromote** | "create a CA policy", "require MFA for X", "promote to enforced" | `Workflows/CreateAndPromote.md` |

## Ground Rules

1. **Never promote to `enabled` without first checking `break-glass-account-audit`** for this tenant — the exclusion check only proves *some* exclusion exists, not that it's a *real*, monitored, non-phishable-MFA break-glass account.
2. **Always review report-only sign-in impact between creation and promotion.** Creation and promotion are two separate confirm-gated calls for exactly this reason — don't collapse them into one prompt turn.
3. Both tools require `ENTRA_ENABLE_WRITES=true` and the `Policy.ReadWrite.ConditionalAccess` delegated scope; if the scope was never consented, promotion will 403 even though creation succeeded — that's an auth gap, not a logic bug.

## Gotchas

- `create_conditional_access_policy`'s `state` default is `enabledForReportingButNotEnforced`, not `disabled` — a caller who omits `state` still gets a policy that evaluates and logs (report-only), just doesn't block. Say this explicitly when previewing the create call so the operator isn't surprised by sign-in log noise.
- The exclusion check in `update_conditional_access_policy_state` only looks at `conditions.users.excludeUsers`/`excludeGroups` on the target policy itself — it does not verify those IDs actually resolve to real, active accounts. Pair with `break-glass-account-audit` before trusting it.
- `graphObjectPath()` URL-encodes the policy ID for both tools — pass the raw Graph object ID, not a pre-encoded one.

## Examples

**Example 1: Require MFA for a new app, staged rollout**
```
User: "Require MFA for the new finance app, but don't turn it on live yet"
→ CreateAndPromote → create_conditional_access_policy (state omitted → report-only) → preview shown → confirm:true
→ Operator reviews report-only sign-in impact for a few days → CreateAndPromote resumes
→ update_conditional_access_policy_state (state: enabled) → refuses unless break-glass exclusions exist → operator adds them → retried → confirm:true → live
```
