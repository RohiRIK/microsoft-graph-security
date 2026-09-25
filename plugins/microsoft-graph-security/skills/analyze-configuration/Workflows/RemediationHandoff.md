---
type: Workflow
title: "Remediation Handoff"
description: "Act on AuditConfigurationDrift findings where a write tool exists; hand everything else to the operator as an explicit action list."
tags: [intune, remediation, write-critical, write-standard, write-destructive]
timestamp: 2026-07-31T00:00:00Z
---

# Remediation Handoff

Takes the findings from `AuditConfigurationDrift` and splits them into two lanes. Never blur
the line between them in a report — an operator reading "remediated" must be able to trust
that a real Graph write happened, not that the model reasoned about a fix.

## Lane 1: Tool-actionable (a write tool actually covers this)

10 write tools now cover naming, lifecycle, and compliance-field corrections across all 4
policy surfaces:

1. **Typo'd/unclear/stale policy name** (any surface) → `update_configuration_policy` (Settings
   Catalog — note: body field is `name`, not `displayName`, and it's a **beta** endpoint),
   `update_device_configuration`, or `update_endpoint_security_policy`. `write_standard`,
   confirm-gated, metadata only — does not touch settings inside the policy.
2. **Legacy/placeholder/duplicate policy that should be removed** (any surface) →
   `delete_configuration_policy` (beta), `delete_device_configuration`,
   `delete_endpoint_security_policy`, or `delete_device_compliance_policy`. `write_destructive`,
   confirm-gated, irreversible — get explicit per-item operator sign-off, never batch-delete
   from a single confirmation, especially for a policy whose real-world purpose isn't obvious
   from its name alone (fix the name first if it's unclear, don't delete a mystery policy).
3. **Wrong Defender-risk-threshold/BitLocker/secure-boot/code-integrity/health-report field on
   an existing compliance policy** → `update_device_compliance_policy`. `write_critical`,
   confirm-gated — can flip already-evaluated devices to noncompliant, same tier as
   `create_device_compliance_policy`.
4. **Stale/behind-version security baseline** → `device-compliance-baseline-provisioning`'s
   `AssignSecurityBaseline` workflow: assign the current template version as a new instance.
   **Do not delete or retire the old instance unless the operator explicitly asks** — leave it
   in place and say plainly that both now exist.
5. **Missing or under-scoped compliance policy** (a gap, not an existing-policy correction) →
   `device-compliance-baseline-provisioning`'s `ProvisionCompliancePolicy` workflow.
6. **Wrong setting value inside an existing Settings Catalog policy** → `create_configuration_policy`.
   This is the create-a-corrected-replacement path, not a patch: read the flawed policy's
   settings (`GET .../configurationPolicies/{id}/settings`), copy every `settingInstance` entry,
   correct the one bad value, and `create_configuration_policy` with the full corrected set,
   assigned to the same group. **The original flawed policy is never touched or deleted** —
   report the new policy's ID and tell the operator the old one is still there, untouched,
   pending their own decision on it. Deleting the old policy requires the operator to say so
   explicitly in a later, separate turn — never infer it from "fix this policy."
7. **Outdated minimum Windows 11 build baseline across compliance policies** →
   `intune.update_compliance_baseline_os`. `write_critical`, confirm-gated — patches
   `osMinimumVersion` across active Windows compliance policies to the specified target build version
   (e.g. `10.0.22631.3880`), raising fleet compliance baselines to modern patch levels.

Preview every one of these individually (no `confirm`) before the `confirm: true` call — never
batch multiple writes under one operator approval, regardless of tier.

## Lane 2: No tool exists — administrator action list

Still genuinely unactionable:

- **In-place setting-value corrections** — no tool patches an existing policy's settings
  directly. `create_configuration_policy` (Lane 1, item 6) is the *replacement* path, not an
  in-place fix; if the operator specifically insists on patching the original object rather
  than creating a replacement, that's still Lane 2 — the per-setting PATCH shape
  (`PATCH .../configurationPolicies/{id}/settings/{settingId}`) is real (confirmed via the
  official Graph reference) but its request body was never tested live, so route to the portal
  instead of guessing.
- **Classic Device Configuration profiles' per-`@odata.type` settings** (190+ possible types,
  each with its own field shape) — only the display name/description is fixable via
  `update_device_configuration`; the settings inside are untouched by any tool, and there is no
  create-a-replacement path for this surface (only Settings Catalog has `create_configuration_policy`).
- **Group Policy Configurations (Administrative Templates)** — same as above; rename/delete
  work via the generic tools if the tenant has any, but individual GPO setting values are not
  reachable.

## Steps

1. Partition the audit findings into Lane 1 / Lane 2 per the rules above.
2. For each Lane 1 item, preview first, get explicit per-item operator approval, then
   `confirm: true` — report the real Graph response back (updated/deleted ID), not a summary
   claim.
3. Compose the Lane 2 list as explicit, numbered administrator tasks, each citing the specific
   finding and its source (Learn-doc citation if available; note if Learn MCP was unreachable
   and the claim is training-knowledge-only, per `AuditConfigurationDrift`'s Ground Rule 2).
4. **Final report**: what was actually changed/deleted (with IDs), what still needs manual
   action (numbered list), and total finding count reconciled against both lanes — no finding
   should disappear silently between the audit and this report.

## Gotchas

- Resist the pressure to "just fix it" when no tool exists — inventing a workaround (e.g. a raw
  Graph call outside the registered tool surface) breaks the two-phase confirm/audit-logging
  guarantee every other write in this codebase has. Route the operator to the portal instead.
- Don't delete a policy just because its name is garbled — rename it first if the operator
  confirms it's real but poorly named; only delete what's confirmed as genuinely obsolete or
  duplicate. A garbled name is a naming-quality finding, not automatically a deletion candidate.
- `update_configuration_policy`/`delete_configuration_policy`/`create_configuration_policy`
  all require `client.betaBaseUrl` — confirmed live that the v1.0 base URL 400s on
  `configurationPolicies` entirely.
- **Never delete the original policy in a create-replacement flow unless the operator
  explicitly says to delete it, in words, in that turn.** "Fix this policy" or "correct the
  setting" is not consent to delete anything — it's consent to create the corrected
  replacement and report back. Two policies existing side by side is the expected, safe
  outcome until the operator says otherwise.
