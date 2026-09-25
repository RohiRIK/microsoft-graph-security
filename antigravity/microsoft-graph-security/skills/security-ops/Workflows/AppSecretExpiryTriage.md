---
type: Workflow
title: "Orphaned App Registration & Secret Expiry Triage"
description: "Find app registrations with expiring credentials, check whether the owner is still active, and route rotation to the right humans. Executable version of operational flow 08."
tags: [security-ops, entra, applications, secrets, hygiene]
timestamp: 2026-07-04T00:00:00Z
---

# App Secret Expiry Triage

Source flow: `docs/operational-flows/08-mailbox-calendar-permissions-audit.md`

## Steps

1. **Sweep for expiring credentials.** Call `entra.audit_credential_hygiene` (or CLI `bun run cli entra apps hygiene --threshold-days 30`). This buckets credentials into expired and expiring secrets/certificates with structured days-until-expiry calculations, eliminating manual app-by-app paging.
2. **Check ownership.** For each expiring app: owner lookup via `entra.get_application` → `entra.get_user` on each owner — `accountEnabled: false` or missing owner = **orphaned**.
3. **Assess blast radius.** `entra.get_service_principal` for the app: granted app roles and enabled state — an orphaned app with Directory or Mail permissions outranks a dormant test app.
4. **Find the humans (best-effort).** For orphaned apps: `entra.get_user_manager` on the departed owner → escalate to their manager; `entra.list_user_direct_reports` on the manager to find the successor team.
5. **Escalate.** `exchange.send_message` (write_critical, two-phase confirm) to the identified lead: app name, appId, expiry date, permissions held, owner status, and the rotation decision needed.
6. **Track.** Summarize the sweep: total expiring, orphaned count, escalations sent, apps needing an ownership decision.

## Capability boundaries

- **No credential rotation tools** (add/remove app secrets, KeyVault injection) — rotation itself is an operator/portal action; this workflow does the discovery, triage, and routing.
- **No Teams/message-trace search** for "who discussed this app" — owner-manager chain (step 4) is the available approximation.
