---
name: device-compliance-baseline-provisioning
description: Create a Windows device compliance policy and assign a Microsoft-maintained security baseline through intune_mcp's write_critical provisioning tools. USE WHEN standing up new device compliance requirements, rolling out a security baseline to a device group, or wiring Defender risk score into compliance evaluation. NOT FOR diagnosing why an existing device is already noncompliant (use security-ops's ComplianceRemediation) or authoring custom baseline settings (out of scope — this tool assigns Microsoft's maintained content as-is).
metadata:
  category: workflow
  effort: medium
  tags: intune, compliance, security-baseline, provisioning, write-critical
---

# device-compliance-baseline-provisioning

Two `intune.*` write_critical tools plus one read tool. Both writes require a mandatory
`group_id` in their schema — there is no "all devices" shortcut, so a new, untested policy
can never accidentally push fleet-wide.

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **ProvisionCompliancePolicy** | "create a compliance policy", "require BitLocker/secure boot for X", "wire Defender risk into compliance" | `Workflows/ProvisionCompliancePolicy.md` |
| **AssignSecurityBaseline** | "assign the Windows security baseline", "roll out MDM baseline to a group" | `Workflows/AssignSecurityBaseline.md` |

## Ground Rules

1. **`assign_security_baseline` uses `list_security_baseline_templates` first** — a real `template_id` is required; there's no way to author a baseline from scratch here, only instantiate Microsoft's maintained one.
2. **Both tools hit `DeviceManagementConfiguration.ReadWrite.All`**, and `assign_security_baseline` specifically calls the **beta** Graph endpoint (`/deviceManagement/templates/{id}/createInstance`, `/deviceManagement/intents/{id}/assign`) — beta endpoints can change shape without notice; re-verify against Microsoft Graph's current docs if either call starts failing unexpectedly.
3. **Researched default for `device_threat_protection_required_security_level` is `low`**, not `medium` — some Microsoft guidance uses `medium` as the noncompliance threshold. `low` is the safer starting point (fewer false negatives); state the tradeoff explicitly if the operator wants to loosen it.

## Gotchas

- **`deviceThreatProtectionEnabled`/`deviceThreatProtectionRequiredSecurityLevel` are silently dropped by Graph on tenants without the Defender for Endpoint↔Intune MDE connector configured** — confirmed live: the field is accepted in the request body (no error) but absent from both the create response and a follow-up GET, while BitLocker/secure boot/code integrity all persist correctly. If a client reports "the Defender risk threshold isn't taking effect," check the MDE connector under Intune → Endpoint security → Connections before assuming the tool is broken.
- Graph requires exactly one `scheduledActionsForRule` entry to create a Windows compliance policy at all (`400 BadRequest: Compliance policy must have one and only one block scheduled action` otherwise) — the tool hardcodes a `block`/0-hour-grace-period default matching the portal's own default; this isn't currently exposed as a schema field.
- Both write tools check for a returned `id` before attempting assignment — if creation succeeds but returns no `id` (malformed response), the tool refuses to assign rather than guessing a target. Don't retry with a manually-supplied ID; investigate the creation response first.
- `create_device_compliance_policy` is Windows-only (`#microsoft.graph.windows10CompliancePolicy`) — Android/iOS compliance policies are a different Graph resource type, not covered by this tool.

## Examples

**Example 1: New client onboarding, compliance policy**
```
User: "Set up baseline Windows compliance for the new client's pilot group"
→ ProvisionCompliancePolicy → create_device_compliance_policy (defaults: threat level low, BitLocker/secure boot/code integrity/health report all true)
→ preview shown → confirm:true → policy created and assigned to the pilot group in one call
```

**Example 2: Security baseline rollout**
```
User: "Assign the Windows security baseline to IT-Pilot-Devices"
→ AssignSecurityBaseline → list_security_baseline_templates (find "MDM Security Baseline for Windows 10 and later")
→ assign_security_baseline (template_id, group_id) → preview → confirm:true
```
