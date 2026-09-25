---
type: Workflow
title: "Phishing Campaign Purge"
description: "From one reported phishing email to campaign scope, mailbox-by-mailbox purge, and threat-intel evidence. Executable version of operational flow 09."
tags: [security-ops, phishing, exchange, defender]
timestamp: 2026-07-03T00:00:00Z
---

# Phishing Campaign Purge

Source flow: `docs/operational-flows/09-phishing-campaign-purge.md`

## Steps

1. **Extract IoCs (agent-side).** Parse the reported `.eml` / pasted headers: sender address + domain, subject, Message-ID, embedded URLs. No tool call — this is analysis.
2. **Check existing detections.** `defender.list_security_alerts` filtered to recent window — Defender for Office 365 may already have alerts for the campaign; `defender.get_security_incident` (expand_alerts) if correlated. `defender.list_threat_indicators` — is the sender domain/URL already known?
3. **Scope the campaign (per-mailbox search).** Requires app-only mode with `Mail.Read.All`. For each target mailbox (start with VIPs and the reporter's team, expand as hits appear):
   - `exchange.search_mail` with the subject / sender / Message-ID.
   - Record mailbox, message id, read/unread state.
   - Note: search is per-mailbox — tenant-wide sweep iterates; respect the rate limiter and report progress in batches.
4. **Who engaged?** For hit mailboxes where the message is read: `entra.list_sign_ins` for those users since delivery time — risky or unfamiliar sign-ins after opening → **RISKY_SIGNIN**, escalate that user to the SpearphishBlastRadius workflow.
5. **Purge (gated, per message).** `exchange.delete_message` (write_destructive, two-phase confirm) for each hit. Preview shows mailbox + subject + message id; batch approvals per 10–20 messages, never blanket-approve silently.
6. **Block the source.** Submitting a tiIndicator is a write — **not available** (defender plane is read-only). Hand the operator the extracted IoCs (domain, URLs, Message-ID pattern) for Defender portal submission / transport rule creation.
7. **Close out.** Summary: mailboxes searched, hits, purged count, users escalated, IoCs handed off. Recommend `entra.revoke_sign_in_sessions` (write_critical, confirm) for any user who entered credentials.

## Flag rules in play

- **RISKY_SIGNIN** — post-open risky sign-in is the pivot from "purge" to "account compromise response."

## Capability boundaries

- **No tenant-wide eDiscovery search** — `exchange.search_mail` is per-mailbox; tenant sweep is an iteration, not one call. For very large tenants, the Purview/eDiscovery portal remains the right tool; this workflow is fastest for targeted campaigns.
- **No threat-indicator submission and no tenant-wide domain block** — defender plane is read-only; mail flow rules are a forbidden action in the exchange backend. Both are operator handoffs with prepared IoCs.
