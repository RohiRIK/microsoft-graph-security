---
name: cloud-security-engineer
description: Correlates across all 5 Graph planes (Entra + Intune + Defender + Exchange + Purview) with risk flags. USE WHEN triaging users/devices, posture scorecards, risky sign-ins, MFA, privilege escalation, offboarding, BEC forwarding, data exfiltration, insider risk, or legal-hold gaps. NOT FOR single-plane lookups.
metadata:
  category: workflow
  effort: medium
  argument-hint: a user, device, or security scenario
---

# Cloud Security Engineer

Five read-only Microsoft Graph MCP servers: **entra_id_mcp** (identity), **intune_mcp**
(devices), **defender_mcp** (security), **exchange_online_mcp** (mail/calendar/rules), and **purview_mcp**
(compliance). Lead with risk — contradictions are the headline.

![Cross-plane correlation workflow](../../assets/workflow-cross-plane-correlation.svg)

## Before anything: name the tenant

Read `gateway://session` and open with the tenant it reports:

> Investigating in **Contoso** (`11111111-…`), delegated as the signed-in user.

Non-negotiable. A consultant runs several clients and the gateway's startup
banner goes to stderr, which the MCP host swallows — so the chat window is the
only place the tenant can appear, and an investigation whose transcript never
names its tenant cannot be handed to a client or re-read six months later.

The allowlist stops you *connecting* to the wrong tenant. Nothing stops you
*believing* you are in a different one you are also allowed to reach. This is
the only guard against that.

If the resource is unavailable, say so and continue — but say it in the opening
line rather than proceeding silently.

## Routing

| Scenario | Call | Then |
|----------|------|------|
| U1: Who's signed in + devices | entra `list_sign_ins` → intune `search_managed_devices` | Correlate + flags |
| U2: Is device compliant? | intune compliance + entra `deviceDetail` | Verdict |
| U3: Fleet sweep | intune `list_managed_devices` + entra `get_user` | All flags |
| U4: Triage user | entra `get_user` + intune `search_managed_devices` | Full triage |
| U5: Risky sign-in | entra `list_sign_ins` (risk≠none) → intune | Risk flags |
| U6: Why noncompliant? | intune `get_managed_device` + compliance policies | Failing policy |
| U7: Phishing investigation | entra `list_sign_ins` + `list_directory_audits` | Timeline |
| U8: MFA weakness | entra `list_sign_ins` + `list_role_assignments` | MFA_WEAK flags |
| U9: Privilege escalation | entra `list_directory_audits` + `list_role_assignments` | PRIV_RISK flags |
| U10: Device offboarding | intune `list_managed_devices` (ORPHAN) + `get_user` | Wipe candidates |
| U15: Data exfiltration | entra `list_sign_ins` + `list_directory_audits` → purview cases/custodians | DATA_EXFIL |
| U16: Insider risk | entra `list_role_assignments` → purview cases/custodians/labels | INSIDER_RISK, HOLD_GAP |
| U17: App privilege & blast radius | entra `audit_app_registrations` + `get_app_blast_radius` | APP_RISK, EXPIRED_CRED |
| U18: Standing PIM dormancy | entra `audit_dormant_pim_eligibility` | DORMANT_PRIV |
| U19: Unscoped mail & SharePoint access | exchange `audit_unscoped_mail_access` + purview `audit_sites_selected` | UNSCOPED_ACCESS |
| U20: Domain SPF posture | exchange `validate_domain_spf` | SPF_MISCONFIG |
| U21: Tenant posture scorecard | `bun run cli triage posture` or all 5 planes audit tools | CRITICAL_RISK, NEEDS_ATTENTION, HEALTHY |
| U22: BEC & Mail forwarding sweep | exchange `audit_forwarding_rules` or `bun run cli triage user` | BEC_FORWARDING |
| U23: Endpoint firewall posture | intune `audit_firewall_policies` or `bun run cli triage device` | FIREWALL_GAP, CLASSIC_PROFILE |
| U24: Threat intelligence & alerts | defender `audit_threat_indicators` | THREAT_ALERT |
| U25: Retention & legal holds audit | purview `audit_retention_cases` | RETENTION_GAP |

## Join Model

Join on: `userPrincipalName` (case-insensitive) · `userId` · Entra `deviceDetail.deviceId` ↔ Intune `azureADDeviceId` · Purview custodian `email` ↔ UPN. Never display name.

## Flag Rules

- **CONTRADICTION** — Entra `deviceDetail.isCompliant` ≠ Intune `complianceState`
- **STALE** — compliant but `lastSyncDateTime` >7 days
- **ORPHAN** — managed device with disabled/absent owner
- **RISKY_SIGNIN** — high-risk sign-in on managed device
- **MFA_WEAK** — privileged user with MFA failures
- **APP_RISK** — enterprise app with critical blast radius score or high-privilege directory permissions
- **HYGIENE_RISK** — enterprise app credentials expired or expiring within 30 days
- **DORMANT_PRIV** — standing PIM directory role eligibility exceeding 90 days
- **UNSCOPED_ACCESS** — application holding tenant-wide `Mail.*` roles or sensitive `Sites.Selected` grants
- **SPF_MISCONFIG** — domain SPF record invalid or exceeding RFC 7208 DNS lookup ceiling (10)
- **PRIV_RISK** — privileged user with noncompliant device
- **OFFBOARD_GAP** — orphaned device with old sync
- **DATA_EXFIL** — risky sign-in / audit burst by a custodian on a non-closed case
- **INSIDER_RISK** — privileged user who is a custodian on a non-closed case
- **HOLD_GAP** — custodian hold not applied, or released while the case is still active
- **BEC_FORWARDING** — unauthorized external forwarding, redirect, or auto-delete message rule on user mailbox
- **FIREWALL_GAP** — zero Windows Firewall policies configured or assigned in Intune
- **CLASSIC_PROFILE** — legacy classic Windows Firewall profile detected instead of Endpoint Security policy
- **THREAT_ALERT** — active high-severity alerts correlated with ingested threat intelligence indicators
- **RETENTION_GAP** — active eDiscovery case or custodian without applied retention/hold coverage

Full procedures: **`PLAYBOOK.md`**.

## Audit Logging

Every invocation logs to `AUDIT.md` (append-only). Log entry includes:
- Timestamp (ISO 8601)
- Question asked
- Scenario triggered (U1-U10, U15-U16)
- Tools called with parameters (redacted IDs)
- Summary of findings (no secrets/tokens)
- Flags fired
- Actions taken

Purpose: Validate skill behavior, ensure no unwanted actions.

## Gotchas

- Single-plane → defer to that MCP only. Over-pulling is #1 misfire.
- `deviceDetail.isCompliant` ≠ `complianceState` — they differ across time. Flag, don't assume bug.
- Read-only. Never call write tools. Never echo tokens/secrets.
- Graceful degradation: one MCP 403s → answer from available plane, state which was missing.
- Always append audit entry after responding — log is the safety net.
- `purview.list_retention_labels` missing is NOT an outage — `RecordsManagement.Read.All` is
  delegated-only, so that tool doesn't exist when purview_mcp runs app-only. Say so and continue.
- eDiscovery data may be legally privileged: report case IDs and hold status, never quote
  search `contentQuery` terms or review-set content into a shared summary.
