---
name: security-ops
description: Execute the repo's IT/SecOps operational flows against the MCP Gateway (entra.*, intune.*, exchange.*, defender.*, purview.*). USE WHEN handling JIT access requests, access-denied triage, compliance remediation, spearphish blast-radius, hostile offboarding, phishing purge, or tenant posture sweeps. NOT FOR single-plane directory queries (use EntraIdOps) or generic cross-plane correlation (use cloud-security-engineer).
metadata:
  category: workflow
  effort: medium
  tags: security-ops, workflows, gateway, entra, intune, exchange, defender, purview
---

# SecurityOps

Executable versions of the business workflows in `docs/operational-flows/`. Each workflow maps plain-language steps to concrete namespaced MCP tool calls through the gateway (`entra.*`, `intune.*`, `exchange.*`, `defender.*`, `purview.*`), names the cross-plane flag rules that apply, and marks every write with its confirmation gate.

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **TenantPostureSweep** | "tenant posture", "security scorecard", "sweep all planes", "cross-plane health" | `Workflows/TenantPostureSweep.md` |
| **JitPrivilegedAccess** | "grant temporary admin", "elevate for ticket", "JIT access", "revoke elevation" | `Workflows/JitPrivilegedAccess.md` |
| **AccessDeniedTriage** | "user can't access app", "access denied", "why is X blocked", "group conflict" | `Workflows/AccessDeniedTriage.md` |
| **ComplianceRemediation** | "device noncompliant", "VPN blocked by compliance", "why is device blocked" | `Workflows/ComplianceRemediation.md` |
| **SpearphishBlastRadius** | "suspicious forwarding rule", "is this account high-value", "blast radius for alert" | `Workflows/SpearphishBlastRadius.md` |
| **HostileOffboarding** | "urgent offboarding", "terminate access now", "lock out departing employee" | `Workflows/HostileOffboarding.md` |
| **PhishingPurge** | "phishing campaign", "purge this email", "who else received this" | `Workflows/PhishingPurge.md` |
| **AutopilotSelfHealing** | "autopilot failed", "provisioning stuck", "wrong deployment profile" | `Workflows/AutopilotSelfHealing.md` |
| **ServicePrincipalContainment** | "service principal anomaly", "app acting weird", "SP compromise" | `Workflows/ServicePrincipalContainment.md` |
| **AppSecretExpiryTriage** | "expiring secrets", "orphaned app", "credential rotation sweep" | `Workflows/AppSecretExpiryTriage.md` |
| **IdentityNetworkCorrelation** | "correlate with network logs", "SIEM handoff", "identity evidence package" | `Workflows/IdentityNetworkCorrelation.md` |

## Ground Rules (apply to every workflow)

1. **Reads are free, writes are gated twice.** Write tools exist only if the backend was started with `*_ENABLE_WRITES=true`, and every destructive/critical write is two-phase: first call without `confirm` returns a preview — show it to the user, get explicit approval, then re-call with `confirm: true`. Never infer approval.
2. **Stay single-plane when the question is single-plane.** Over-pulling is the #1 misfire (HANDOFF §GOTCHAS).
3. **Join model:** correlate on `userPrincipalName` (case-insensitive), `userId`, Entra `deviceDetail.deviceId` ↔ Intune `azureADDeviceId`.
4. **Flag rules** (from `skills/cloud-security-engineer/`): CONTRADICTION, STALE, ORPHAN, RISKY_SIGNIN, MFA_WEAK, PRIV_RISK, OFFBOARD_GAP, BEC_FORWARDING, FIREWALL_GAP, HYGIENE_RISK. Emit them in summaries whenever the evidence triggers one.
5. **Graceful degradation:** if one backend returns 403, answer from the available planes and say which plane was missing.
6. **Capability boundaries are documented, not improvised.** Each workflow lists steps that have no tool yet — those are handed to the operator as explicit manual actions, never silently skipped and never simulated.
7. **Defender containment and hunting capabilities**: Defender provides confirm-gated machine isolation (`defender.isolate_device`), file hash indicator blocking (`defender.block_file_indicator`), structured evidence extraction (`defender.get_alert_evidence`), and Advanced Hunting KQL queries (`defender.run_hunting_query`). Writes are gated behind `DEFENDER_ENABLE_WRITES=true` and `confirm: true`.

## Quick Reference — write tools by plane

| Plane | Write tool | Risk | Use |
|-------|-----------|------|-----|
| entra | `entra.update_user` | write_standard | disable account (`accountEnabled: false`) |
| entra | `entra.add_group_member` / `entra.remove_group_member` | write_standard/destructive | group-based access grants/revocations |
| entra | `entra.revoke_sign_in_sessions` | write_critical | kill refresh tokens tenant-wide for a user |
| entra | `entra.reset_user_auth_methods` | write_critical | remove non-password MFA methods & revoke sessions |
| entra | `entra.disable_application` | write_destructive | disable compromised service principal |
| intune | `intune.remote_lock_device` | write_destructive | lock a compromised endpoint |
| intune | `intune.wipe_device` / `intune.retire_device` | write_critical/destructive | corporate data removal |
| exchange | `exchange.delete_message` | write_destructive | purge a specific message from a mailbox |
| exchange | `exchange.send_message` | write_critical | operator notifications |
| defender | `defender.isolate_device` | write_critical | network isolation of compromised machine |
| defender | `defender.block_file_indicator` | write_critical | submit alertAndBlock threat indicator for file hash |

## Gotchas

- **Every tool call is recorded now, reads included.** Before 2026-08-09 only writes were, so
  the audit log was empty by construction in a read-only product. A workflow that cites audit
  rows will find nothing in logs written before that.
- **A finding is only as good as the tenant it came from.** Confirm `gateway://session` names
  the client you think you are investigating — settings resolve at startup, and a session can
  outlive the profile it was started with.
- **Read tools are `read_sensitive` for a reason.** Their output carries directory PII; a
  write-up made from them should be masked unless the recipient is entitled to see it
  (`bun run investigate` masks by default).
