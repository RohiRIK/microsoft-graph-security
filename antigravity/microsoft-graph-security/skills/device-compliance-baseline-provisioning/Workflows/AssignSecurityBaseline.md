---
type: Workflow
title: "Assign a Microsoft Security Baseline"
description: "Find a maintained baseline template and assign an instance of it to a device group."
tags: [intune, security-baseline, beta-endpoint]
timestamp: 2026-07-31T00:00:00Z
---

# Assign Security Baseline

## Steps

1. `intune.list_security_baseline_templates` — find the target template (e.g. "MDM Security Baseline for Windows 10 and later") and note its `id`.
2. **Gather**: instance display name, target `group_id` (mandatory).
3. `intune.assign_security_baseline` without `confirm` — preview shown (template name + target group).
4. Operator approves → re-call with `confirm: true`. Tool creates the baseline instance via `createInstance` (beta), then assigns it to `group_id` via `/deviceManagement/intents/{id}/assign` (also beta) — if instance creation returns no `id`, assignment is not attempted.
5. Report the instance ID and assignment back to the operator.

## Gotchas

- Both Graph calls in this workflow are **beta** endpoints. If either starts returning an unexpected shape, don't assume the tool is broken — check whether Microsoft changed the beta contract first.
- This assigns Microsoft's maintained baseline content **as-is** — no per-setting customization. If the operator wants a modified baseline, that's a manual Intune portal task (clone + edit), not something this tool does.

## Capability boundaries

- No tool lists what settings a given baseline template actually contains — `list_security_baseline_templates` only returns metadata (name, version, platform). Point the operator to the Intune portal to review baseline content before assigning if they haven't used this template before.
