---
type: Workflow
title: "Compliance Remediation (Root-Cause First)"
description: "Find exactly which compliance policy is blocking a device and drive remediation with minimal user friction. Executable version of operational flow 04."
tags: [security-ops, intune, compliance, devices]
timestamp: 2026-07-03T00:00:00Z
---

# Compliance Remediation

Source flow: `docs/operational-flows/04-stale-device-cleanup.md`

## Steps

1. **Find and triage the device.** Query `intune.search_managed_devices` by UPN (or run `bun run cli triage device <deviceId>` for an immediate cross-plane snapshot). Extract `complianceState`, `lastSyncDateTime`, encryption state, and OS version.
2. **Root-cause the block.**
   - `intune.list_device_compliance_policies` → `intune.get_device_compliance_policy` for policies scoped to the device's platform — compare each rule (min OS version, encryption, defender status) against the device record.
   - Audit firewall posture via `intune.audit_firewall_policies` (or `bun run cli intune security firewall`) to verify if the device lacks an assigned Endpoint Security Firewall policy or is caught in legacy classic profile drift.
   - Cross-check `intune.list_audit_events` for recent policy changes that could explain a sudden block.
   - If the failure looks update-related: `intune.list_windows_quality_update_profiles` / `intune.list_windows_feature_update_profiles` for pending deployments; `intune.list_device_health_scripts` / `intune.list_device_compliance_scripts` for remediation scripts already targeting the gap.
3. **Check staleness first.** If `lastSyncDateTime` > 7 days, the compliance verdict itself may be stale (**STALE** flag) — the fix may be simply a device check-in, not a policy change.
4. **Cross-plane sanity.** `entra.list_sign_ins` (deviceDetail) for the same device: if Entra says `isCompliant: true` while Intune says noncompliant → **CONTRADICTION** flag; report both timestamps, do not assume either is a bug.
5. **Remediate.**
   - Device-side sync/remediation push: **no tool — manual step** (see boundaries). Tell the operator exactly which action to trigger in the Intune portal (sync, or the specific remediation script from step 2).
   - Notify the user via `exchange.send_message` (write_critical, two-phase confirm): "Deploying missing update in the background, access restores in ~5 minutes."
6. **Verify.** Re-run `intune.get_managed_device` after sync; confirm `complianceState` flipped and tell the user.

## Flag rules in play

- **STALE** — compliant/noncompliant verdict with `lastSyncDateTime` > 7 days.
- **CONTRADICTION** — Entra `deviceDetail.isCompliant` ≠ Intune `complianceState`.

## Capability boundaries

- **No device-sync or script-trigger write tool.** Intune writes are wipe/retire/lock/passcode/create-app only. The actual "push sync + trigger deployment evaluation" is an operator portal action — the workflow's value is handing the operator the *exact* failing policy and the exact remediation to trigger.
