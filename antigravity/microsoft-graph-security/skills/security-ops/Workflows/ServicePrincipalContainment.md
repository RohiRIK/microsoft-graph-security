---
type: Workflow
title: "Service Principal Behavioral Triage"
description: "Baseline a service principal's normal behavior from sign-in/audit history and map anomalous deviation for containment. Executable version of operational flow 06."
tags: [security-ops, entra, defender, service-principal, incident-response]
timestamp: 2026-07-04T00:00:00Z
---

# Service Principal Behavioral Triage

Source flow: `docs/operational-flows/06-threat-correlation-siem.md`

## Steps

1. **Pull the detection.** `defender.list_security_alerts` / `defender.get_security_incident` (expand_alerts) — extract the service principal's appId/objectId.
2. **Identify the principal.** `entra.get_service_principal` (granted OAuth2 app roles, publisher, enabled state) + `entra.get_application` for the owning registration.
3. **Baseline normal behavior (30 days).**
   - `entra.list_sign_ins` filtered to the SP — locations, resources, volumes.
   - `entra.list_directory_audits` — configuration changes on the SP itself (new credentials, new permissions = classic escalation precursor).
4. **Map the deviation.** Compare granted app roles vs the resource the anomalous calls target (e.g. historical SharePoint reads vs new mailbox enumeration). State it precisely.
5. **Contain (confirm-gated execution).**
   - Disable the compromised SP: call `entra.disable_application` (`write_destructive`, two-phase confirm). First call with `dry_run: true` or without `confirm` returns preview; execute with `confirm: true` upon operator sign-off.
   - If a *user* account is implicated in the chain (owner or actor in the audit trail): `entra.revoke_sign_in_sessions` and `entra.reset_user_auth_methods` (write_critical, two-phase confirm).
6. **RCA report.** Timeline: credential/permission changes → first anomalous sign-in → targeted resources → containment actions taken and pending.

## Flag rules in play

- **PRIV_RISK** — an SP with high-privilege app roles deviating from baseline is the highest-severity finding this workflow produces.

## Capability boundaries

- **Service principal secret/certificate removal** is an operator action in the portal; `entra.disable_application` handles immediate revocation by flipping `accountEnabled: false`.
