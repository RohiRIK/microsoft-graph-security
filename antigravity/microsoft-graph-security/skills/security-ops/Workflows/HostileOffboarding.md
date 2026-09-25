---
type: Workflow
title: "Hostile Offboarding (Identity → Device → Mailbox)"
description: "Synchronized lockout of a departing employee: revoke sessions, disable account, wipe corporate data, preserve mailbox evidence. Executable version of operational flow 07."
tags: [security-ops, offboarding, entra, intune, exchange]
timestamp: 2026-07-03T00:00:00Z
---

# Hostile Offboarding

Source flow: `docs/operational-flows/07-deprovisioned-asset-recovery.md`

> Speed matters here, but every write below is still two-phase confirm. Batch the previews, get one explicit operator approval for the whole sequence, then execute in order.

## Steps

1. **Confirm the target & pre-flight readiness.**
   - Run `bun run cli triage offboard <upn>` to perform an immediate cross-plane offboarding readiness check. This inspects assigned directory roles, managed device wipe candidates, and automatically queries Purview eDiscovery cases to detect whether the user is an active custodian under legal hold (**HOLD BLOCKER**).
   - `entra.get_user` by UPN — verify identity, note `accountEnabled`, `id`. Echo displayName + department back to the operator before any write.
2. **Identity lockout (order matters).**
   1. `entra.update_user` `accountEnabled: false` (write_standard, confirm) — blocks new sign-ins.
   2. `entra.revoke_sign_in_sessions` (write_critical, confirm) — invalidates existing refresh tokens.
   3. `entra.reset_user_auth_methods` (write_critical, confirm) — removes non-password MFA authentication methods, preventing re-registration or bypass.
3. **Access inventory.** `entra.list_user_groups` + `entra.list_role_assignments` — remove privileged/role-assignable memberships via `entra.remove_group_member` (write_destructive, confirm each).
4. **Device sweep.** `intune.search_managed_devices` by UPN → for each device, choose:
   - Corporate-owned: `intune.wipe_device` (write_critical, confirm).
   - BYOD: `intune.retire_device` (write_destructive, confirm) — removes corporate data only.
5. **Mailbox evidence & exfiltration capture.**
   - `exchange.audit_forwarding_rules` (or `bun run cli exchange mail forwarding`): audit and log any inbox rules configured to forward, redirect, or auto-delete messages (crucial evidence of data exfiltration or BEC sabotage prior to departure).
   - `exchange.get_mailbox_info`, `exchange.list_mail_folders` — snapshot state for the record.
   - Litigation hold + shared-mailbox conversion: **no tool — operator action** (see boundaries). Hand the operator the exact target UPN and required hold settings.
6. **Verify + report.**
   - `entra.list_sign_ins` for the user post-lockout — must show only failures.
   - `intune.list_managed_devices` — devices show wipe/retire pending.
   - **OFFBOARD_GAP** check: any managed device still active with the disabled owner → flag and repeat step 4.
   - Summarize timeline with object IDs for the HR/legal record.

## Flag rules in play

- **ORPHAN** / **OFFBOARD_GAP** — devices left behind after account disable are the exact failure mode this workflow exists to prevent.

## Capability boundaries

- **No password-reset tool** — `entra.update_user` covers profile/accountEnabled; credential reset is an operator action.
- **No litigation hold / shared-mailbox conversion tools** — deleting mailboxes and modifying mailbox permissions are forbidden actions in the exchange backend. Legal-hold placement is a documented manual step for the Legal/Exchange admin.
