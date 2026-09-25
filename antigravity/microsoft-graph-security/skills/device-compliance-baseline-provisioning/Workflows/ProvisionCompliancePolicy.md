---
type: Workflow
title: "Provision a Windows Device Compliance Policy"
description: "Create and assign a Windows compliance policy with the researched Defender-risk/BitLocker/secure-boot field set."
tags: [intune, compliance]
timestamp: 2026-07-31T00:00:00Z
---

# Provision Compliance Policy

## Steps

1. **Gather**: display name, target `group_id` (mandatory — no fleet-wide shortcut), and any overrides to the defaults below.
2. **Defaults** (from `docs/best-practices/security-baselines.md`): `device_threat_protection_required_security_level: low`, `bit_locker_enabled`/`secure_boot_enabled`/`code_integrity_enabled`/`require_healthy_device_report`: all `true`.
3. `intune.create_device_compliance_policy` without `confirm` — preview shown (policy name + target group).
4. Operator approves → re-call with `confirm: true`. Tool creates the policy, then assigns it to `group_id` in the same call — if creation returns no `id`, the tool refuses to assign and reports the failure rather than guessing.
5. Confirm result: report the policy ID and group assignment back to the operator.

## Flag rules in play

- If the operator asks to loosen `device_threat_protection_required_security_level` below `low` (e.g. `unavailable`), flag this explicitly as disabling the Defender-risk compliance signal — confirm intent before proceeding.

## Capability boundaries

- No tool exists to preview compliance impact against the *current* device fleet before assigning — assignment is immediate for devices already in the target group. Recommend a small pilot group first for anything but a greenfield tenant.
