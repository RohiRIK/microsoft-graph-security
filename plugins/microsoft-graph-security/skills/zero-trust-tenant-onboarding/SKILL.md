---
name: zero-trust-tenant-onboarding
description: Run the researched phased sequence (CA report-only → device compliance → security baseline → CA promotion) for standing up a brand-new client's security posture. USE WHEN onboarding a new client/tenant from scratch, or asked for 'the whole Zero Trust setup' rather than a single policy. NOT FOR a single ad-hoc CA policy or compliance policy (use conditional-access-provisioning / device-compliance-baseline-provisioning directly) or ongoing posture monitoring of an already-onboarded tenant (use defender-posture-reporting / cloud-security-engineer).
metadata:
  category: workflow
  effort: high
  tags: entra, intune, defender, onboarding, zero-trust, orchestration
---

# zero-trust-tenant-onboarding

Orchestrates `conditional-access-provisioning` and `device-compliance-baseline-provisioning` in
the sequence extracted from `docs/best-practices/entra-intune-defender-integration.md` §4.
This is deliberately **not** a single mega-tool — each phase is its own confirm-gated call,
so the operator judges impact between phases instead of one blanket approval covering
everything.

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **PhasedRollout** | "onboard this new client", "set up the whole baseline", "Zero Trust rollout for a new tenant" | `Workflows/PhasedRollout.md` |

## Ground Rules

1. **Order matters**: security baseline + device compliance land before any CA policy is promoted to `enabled` — a CA policy that requires `compliantDevice` promoted before compliance policies exist locks out everyone immediately.
2. **Break-glass accounts must exist and be verified before phase 4** (CA promotion) — run `break-glass-account-audit` as a hard gate, not a suggestion.
3. **Every phase is its own operator confirmation** — never batch multiple `confirm: true` calls without the operator reviewing each phase's outcome first.

## Gotchas

- This workflow assumes a genuinely new/greenfield tenant. Running it against a tenant that already has CA policies or compliance policies risks duplicate/conflicting policies — check `entra.list_conditional_access_policies` and `intune.list_device_compliance_policies` first and stop if the tenant isn't actually greenfield.
- ASR rules and BitLocker encryption-enforcement profiles are explicitly **out of scope** — no tool exists yet for Settings Catalog's nested `settingInstance` schema; hand these to the operator as manual portal steps per `docs/best-practices/asr-rules.md` / `bitlocker.md`.

## Examples

**Example 1: New client kickoff**
```
User: "Onboard Acme Corp — set up their full Entra/Intune baseline"
→ PhasedRollout → checks tenant is greenfield → security baseline assigned (pilot group)
→ device compliance policy created+assigned (pilot group) → break-glass-account-audit run
→ CA policy created (report-only) → operator reviews impact → CA promoted to enabled
```
