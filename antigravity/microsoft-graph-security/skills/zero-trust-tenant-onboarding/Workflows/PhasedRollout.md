---
type: Workflow
title: "Phased Zero Trust Rollout for a New Tenant"
description: "Baseline → compliance → break-glass audit → CA report-only → CA promotion, one confirmed phase at a time."
tags: [entra, intune, onboarding, orchestration]
timestamp: 2026-07-31T00:00:00Z
---

# Phased Rollout

Source research: `docs/best-practices/entra-intune-defender-integration.md` §4.

## Steps

1. **Greenfield check.** `entra.list_conditional_access_policies` + `intune.list_device_compliance_policies` — if either returns existing custom policies, stop and confirm with the operator whether this is truly a new rollout or an incremental change (route to the single-tool skills instead if incremental).
2. **Phase 1 — Security baseline.** Delegate to `device-compliance-baseline-provisioning`'s `AssignSecurityBaseline` workflow, targeting a pilot device group first, not "all devices."
3. **Phase 2 — Device compliance policy.** Delegate to `device-compliance-baseline-provisioning`'s `ProvisionCompliancePolicy` workflow, same pilot group. This must land before phase 4 if the CA policy will require `compliantDevice`.
4. **Phase 3 — Break-glass audit.** Run `break-glass-account-audit` in full. Do not proceed to phase 5 if it reports zero verified break-glass accounts.
5. **Phase 4 — CA policy, report-only.** Delegate to `conditional-access-provisioning`'s `CreateAndPromote` workflow, stopping after the create step — do not promote yet.
6. **Observation window.** Ask the operator to review report-only sign-in impact for a representative period (days, not minutes) before continuing.
7. **Phase 5 — CA promotion.** Resume `CreateAndPromote`'s promote step, `confirm: true` only after the operator explicitly signs off on the observation window.
8. **Report.** Summarize what's live, what's still pilot-scoped, and what remains manual (ASR rules, BitLocker enforcement — see Gotchas in SKILL.md).

## Flag rules in play

- Refuse to run phase 5 in the same turn as phase 4 — the whole point of the phased design is a human decision point between them.

## Capability boundaries

- ASR rule creation and BitLocker enforcement profiles have no tool yet (Settings Catalog schema not yet built) — always end the report by naming these as manual next steps, never silently omit them.
