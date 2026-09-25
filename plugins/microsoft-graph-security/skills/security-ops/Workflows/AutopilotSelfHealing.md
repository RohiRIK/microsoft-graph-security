---
type: Workflow
title: "Autopilot Provisioning Triage"
description: "Diagnose Autopilot provisioning failures, identify the correct deployment profile from the user's org context, and hand the operator the exact fix. Executable version of operational flow 03."
tags: [security-ops, intune, autopilot, provisioning]
timestamp: 2026-07-04T00:00:00Z
---

# Autopilot Provisioning Triage

Source flow: `docs/operational-flows/03-compliance-contradiction-audit.md`

## Steps

1. **Detect / confirm the failure.** `intune.list_audit_events` (recent window) for enrollment/Autopilot activity; `intune.list_enrollment_configurations` for the applicable enrollment restrictions.
2. **Locate the device record.** `intune.list_windows_autopilot_devices` → `intune.get_autopilot_device` (serial, group tag, assigned profile state).
3. **Determine the intended profile.** `entra.get_user` (department, role) for the assigned user; `intune.list_autopilot_deployment_profiles` — match the profile the user *should* receive against the group tag actually on the record.
4. **Report the mismatch.** State: device serial, current group tag, expected group tag/profile, and the evidence chain.
5. **Fix (operator handoff).** Group-tag update and forced device sync have no write tools — hand the operator the exact device serial + correct tag for the Intune portal action.
6. **Verify.** Re-run `intune.get_autopilot_device` after the operator applies the change; confirm profile assignment flipped.

## Capability boundaries

- **No Autopilot write tools** (group-tag update, profile assignment, device sync). This workflow's value is compressing the diagnosis from hours of portal-hopping to one evidence-backed handoff.
