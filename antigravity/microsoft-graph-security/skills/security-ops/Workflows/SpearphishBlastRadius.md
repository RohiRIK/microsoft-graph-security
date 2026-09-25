---
type: Workflow
title: "Spearphish Blast-Radius Enrichment"
description: "Turn a raw alert on a mailbox into a business-context risk verdict (proximity to leadership, sensitive calendar context, device anomalies) and gated containment. Executable version of operational flow 05."
tags: [security-ops, defender, spearphishing, blast-radius, cross-plane]
timestamp: 2026-07-03T00:00:00Z
---

# Spearphish Blast-Radius Enrichment

Source flow: `docs/operational-flows/05-compromised-endpoint-isolation.md`

## Steps

1. **Pull the alert & extract evidence.** `defender.list_security_alerts` (severity/status/created_after filters) → `defender.get_security_alert` for the specific alert; `defender.get_security_incident` with `expand_alerts: true` if part of an incident. Call `defender.get_alert_evidence` to extract structured entities (users, machines, file hashes, process command lines). Correlate with active threat intelligence via `defender.audit_threat_indicators`. For broad investigation, run targeted KQL queries via `defender.run_hunting_query`. Extract affected UPN and machine ID.
2. **Org proximity.** `entra.get_user` → walk `entra.get_user_manager` upward (2–3 hops): is this account <2 steps from the CEO/CFO? `entra.list_user_direct_reports` for span of influence. `entra.list_role_assignments` — any admin role makes this automatic **PRIV_RISK** territory.
3. **Sensitive context & exfiltration audit.**
   - `exchange.list_calendar_events` for the user, next 14 days (subjects/organizers only — content is redacted): board meetings, M&A keywords, legal reviews raise the score.
   - `exchange.audit_forwarding_rules` (or `bun run cli exchange mail forwarding`): audit inbox message rules for unauthorized external forwarding, message redirection, or auto-deletion rules (**BEC_FORWARDING** flag).
4. **Device posture.** `intune.search_managed_devices` by UPN: recent enrollments (`enrolledDateTime` in last 7 days is anomalous), `complianceState`, `lastSyncDateTime`. `entra.list_sign_ins` for risk state and unfamiliar locations → **RISKY_SIGNIN**.
5. **Score and report.** LOW / MEDIUM / HIGH with the specific evidence lines. HIGH = (proximity ≤2 to exec OR privileged role) AND (risky sign-in OR anomalous enrollment OR BEC forwarding rule).
6. **Contain (gated, HIGH only).**
   - `entra.revoke_sign_in_sessions` (write_critical, two-phase confirm) — kills refresh tokens.
   - `entra.update_user` `accountEnabled: false` (write_standard, confirm) if operator approves full lockout.
   - `intune.remote_lock_device` (write_destructive, confirm) for the affected endpoint.
   - `defender.isolate_device` (write_critical, confirm) — network-isolate the affected endpoint via Defender for Endpoint API (Full or Selective).
   - `defender.block_file_indicator` (write_critical, confirm) — submit `alertAndBlock` threat intelligence indicator for observed malicious file hashes.

## Flag rules in play

- **RISKY_SIGNIN**, **PRIV_RISK**, **BEC_FORWARDING** — all feed the risk score directly.

## Capability boundaries

- **Rule removal is manual:** Inbox forwarding rules can be audited and snapshotted via `exchange.audit_forwarding_rules` (or `bun run cli exchange mail forwarding`). Direct mutation or stripping of inbox rules is not an MCP tool; rule removal is performed by the operator in Exchange admin center, or individual phishing messages can be purged using `exchange.delete_message`.
