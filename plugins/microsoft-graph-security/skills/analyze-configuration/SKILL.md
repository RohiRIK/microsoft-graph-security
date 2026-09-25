---
name: analyze-configuration
description: Inventories Intune device configuration/compliance/endpoint-security policies, cross-references them against Microsoft Learn (learn.*) and this repo's baselines to find legacy settings, drift, duplicate/conflicting policies, and outdated naming — then renames, deletes or field-corrects a policy, creates a corrected replacement when a value is wrong, or hands the operator an action list where no tool exists. USE WHEN auditing device configuration health, asked 'are our device policies up to date', hunting configuration drift, migrating legacy Device Configuration profiles to Settings Catalog, 'fix this policy's name', 'delete this legacy/duplicate policy', or 'correct the compliance requirements/settings on this policy'. NOT FOR why one specific device is noncompliant (use security-ops), or creating a compliance policy from scratch (use device-compliance-baseline-provisioning).
metadata:
  category: workflow
  effort: high
  tags: intune, configuration, drift, legacy-settings, learn-mcp, consolidation
---

# analyze-configuration

Reads across every `intune.*` configuration surface (Settings Catalog `configuration_policies`,
legacy `device_configurations`, `group_policy_configurations`, `endpoint_security_policies`,
compliance policies, security baseline templates), cross-checks against Microsoft Learn via the
gateway's `learn.*` tools, and reports drift/legacy/duplication findings. **Remediation now has
real tools**: rename (`update_configuration_policy`, `update_device_configuration`,
`update_endpoint_security_policy`) and delete (`delete_configuration_policy`,
`delete_device_configuration`, `delete_endpoint_security_policy`,
`delete_device_compliance_policy`) exist for all 4 surfaces, a full curated-field update
(`update_device_compliance_policy`) for compliance policies, and `create_configuration_policy`
for Settings Catalog. **A wrong setting value inside an existing policy is fixed by creating a
corrected replacement (`create_configuration_policy`) — never by patching the original in
place.** The original is left untouched; deleting it requires the operator to explicitly say
so, separately, never inferred from a request to "fix" or "correct" a policy.

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **AuditConfigurationDrift** | "audit device configs", "check for configuration drift", "are our policies current" | `Workflows/AuditConfigurationDrift.md` |
| **RemediationHandoff** | "fix what you found", "remediate the drift", "migrate legacy settings" | `Workflows/RemediationHandoff.md` |

## Ground Rules

1. **Legacy vs modern is a real, named Microsoft distinction**: `device_configurations` (classic Device Configuration Profiles, including Administrative Templates via `group_policy_configurations`) are being superseded by `configuration_policies` (Settings Catalog). A policy present only in the legacy surface with a Settings Catalog equivalent is a migration candidate, not automatically wrong.
2. **Verify every "deprecated" or "renamed" claim against `learn.microsoft_docs_search`/`learn.microsoft_docs_fetch` before reporting it** — Microsoft's own naming and deprecation timelines change; don't rely on training-data memory for something a live doc fetch can confirm.
3. **Setting-level inspection and conflict detection is powered by `intune.index_policy_settings`**: It flattens nested setting instances across configuration policies into `{ settingId, definitionId, value, assignedPolicies: [] }` and flags conflicting values across assigned groups. Attack Surface Reduction rule coverage across Defender baseline policies is audited via `intune.audit_asr_rules`. Proactive remediations and Autopatch run states (with blocker IDs like `POL-08`, `DEV-02`) are checked via `intune.get_autopatch_remediation_status`. Windows 11 OS baseline version requirements are updated across compliance policies via `intune.update_compliance_baseline_os`.
4. **Duplicate/conflicting policy detection** = same target group appearing in `get_*_assignments` for more than one policy of the same type, or overlapping setting definitions holding conflicting values detected by `intune.index_policy_settings` — flag for operator review; delete tools exist now, but never delete a duplicate without the operator confirming which copy to keep.
5. **Rename/delete are confirm-gated, real, in-place fixes** — a naming or duplicate finding is now genuinely fixable, not just reportable. Always preview (no `confirm`) and get explicit sign-off before the second, `confirm: true` call, same as every other write tool in this codebase.
6. **A setting-value fix is always create-new-not-patch, and never deletes the original.** `create_configuration_policy` builds a corrected replacement from a copy of the flawed policy's real settings (one value corrected); it never touches the source policy. Report the new policy's ID and state plainly that the old one is untouched — retiring/deleting it is a separate, explicit operator decision, never bundled into the same confirmation.
7. **Compliance OS baseline version bumps are automated**: `intune.update_compliance_baseline_os` updates `osMinimumVersion` across Windows 10/11 compliance policies with a two-phase confirmation gate.

## Gotchas

- **Settings Catalog policies use `name`, not `displayName`** — `update_configuration_policy`/`create_configuration_policy` send `{ name, ... }`, unlike every other rename/create tool here which uses `{ displayName, ... }`. Confirmed live: sending `displayName` to `configurationPolicies` returns `400 Invalid patch, at least 1 valid property must be changed. Valid properties are Name, Description, RoleScopeTagIds.`
- **`configurationPolicies` (Settings Catalog) is beta-only** — `update_configuration_policy`, `delete_configuration_policy`, and `create_configuration_policy` all require `client.betaBaseUrl`; the v1.0 base URL returns `400 Resource not found for the segment 'configurationPolicies'`. Confirmed live.
- `create_device_compliance_policy` requires a hardcoded `scheduledActionsForRule` (Graph rejects creation without it) and its `deviceThreatProtectionEnabled`/`RequiredSecurityLevel` fields are silently dropped by Graph on tenants without the Defender-for-Endpoint↔Intune connector — confirmed live in `device-compliance-baseline-provisioning`. The same caveat applies to `update_device_compliance_policy`.
- `assign_security_baseline` only instantiates Microsoft's maintained baseline **as-is** — it cannot "correct" a specific misconfigured setting inside an existing baseline instance; the remediation path for a stale baseline is assign the current template version, not patch the old instance (and don't delete the old instance without explicit operator sign-off, same rule as everywhere else).
- **`create_configuration_policy`'s `settings` array must be real, verified `settingInstance` objects** — typically obtained by reading the flawed policy's own settings first (`GET .../configurationPolicies/{id}/settings`), not authored from scratch. A guessed `settingDefinitionId` fails silently rather than erroring.
- The gateway's Learn MCP tools (`learn.microsoft_docs_search`/`microsoft_docs_fetch`) were broken earlier this session (`gateway_mcp/src/index.ts` hardcoded every proxied tool's `inputSchema` to `z.object({})`, discarding each backend's real schema) — **fixed** via `fromJsonSchema()`, verified live with a real search returning real results. If it ever returns empty results again, suspect this same class of bug before assuming the query is wrong.

## Examples

**Example 1: Quarterly configuration health check**
```
User: "Audit our device configs — anything outdated or conflicting?"
→ AuditConfigurationDrift → inventories all policy types → cross-checks 2 legacy findings against learn.microsoft_docs_search
→ Reports: 1 legacy GPO-style profile with a Settings Catalog equivalent, 1 duplicate assignment, baseline template is 3 versions behind current
```

**Example 2: Fix a misconfigured Settings Catalog policy**
```
User: "This policy's BitLocker setting is wrong, fix it"
→ RemediationHandoff → reads the policy's real settings, copies them with the one value corrected
→ create_configuration_policy (confirm-gated) → new policy created and assigned to the same group
→ Reports: new policy ID; original policy left untouched — "delete the old one?" is a separate question, not asked or assumed
```
