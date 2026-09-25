---
type: Workflow
title: "Audit Configuration Drift"
description: "Inventory every Intune configuration surface, cross-check against Microsoft Learn, and report drift/legacy/duplication findings."
tags: [intune, configuration, drift, learn-mcp]
timestamp: 2026-07-31T00:00:00Z
---

# Audit Configuration Drift

## Steps

1. **Inventory every configuration surface**:
   - `intune.list_configuration_policies` (Settings Catalog — modern)
   - `intune.list_device_configurations` (classic Device Configuration Profiles — legacy-capable)
   - `intune.list_group_policy_configurations` (Administrative Templates — legacy)
   - `intune.list_endpoint_security_policies`
   - `intune.list_device_compliance_policies`
   - `intune.list_security_baseline_templates`
2. **Legacy-vs-modern check**: for each `device_configurations`/`group_policy_configurations` entry, note its platform and purpose. Use `learn.learn_microsoft_docs_search` (query the specific profile type, e.g. "Windows Administrative Templates Intune deprecated Settings Catalog") to confirm whether Microsoft currently recommends a Settings Catalog migration for it — don't assert deprecation from memory alone.
3. **Naming convention check**: compare each policy's `displayName` against current Microsoft-recommended naming patterns (fetch via `learn.learn_microsoft_docs_fetch` if the operator has a specific naming standard doc, otherwise flag only clearly stale patterns — e.g. references to product names Microsoft has since renamed).
4. **Duplicate/conflicting assignment check**: for each policy type, pull `get_*_assignments` and group by target `groupId`. Flag any group appearing under more than one policy of the same category (e.g. two compliance policies both targeting `All Devices`) as a consolidation candidate.
5. **Baseline currency check**: compare the `versionInfo` returned by `list_security_baseline_templates` against the latest version referenced in current Microsoft Learn docs for that baseline — flag if behind.
6. **Setting-level conflict indexing**: call `intune.index_policy_settings` to flatten all setting instances across configuration policies into `{ settingId, definitionId, value, assignedPolicies: [] }`. Flag any setting ID that has conflicting values across assigned groups.
7. **Attack Surface Reduction (ASR) rules audit**: call `intune.audit_asr_rules` to evaluate the 16 core ASR rules against active Defender baseline policies, reporting coverage gaps and rules set to audit vs block.
8. **Proactive remediations & Autopatch health**: call `intune.get_autopatch_remediation_status` to detect issues (`lastState eq 'issueDetected'`) and extract blocker IDs (`POL-08`, `DEV-02`).
9. **Compose the report**: per finding — category (legacy / drift / duplicate / setting-conflict / asr-gap / autopatch-issue / stale-naming / stale-baseline), affected policy, Learn-doc citation backing the claim, and recommended action. Explicitly separate "tool-actionable" findings from "administrator review required" findings — the next workflow (`RemediationHandoff`) acts on the former.

## Flag rules in play

- **CONFIG_DRIFT** — legacy profile with a confirmed modern equivalent, or baseline template behind current version.
- **POLICY_CONFLICT** — same target group under multiple same-category policies, or setting-level conflict detected by `index_policy_settings`.
- **NAMING_STALE** — policy name references deprecated product/branding terminology.
- **ASR_GAP** — one or more of the 16 core ASR rules unconfigured or set to audit-only.
- **AUTOPATCH_BLOCKED** — Proactive remediation reporting detection failures (`POL-08`, `DEV-02`).

## Capability boundaries

- `intune.index_policy_settings` inspects Settings Catalog configuration policies. Custom mobile device management (OMA-URI) profiles require manual inspection of raw XML/URI values.
