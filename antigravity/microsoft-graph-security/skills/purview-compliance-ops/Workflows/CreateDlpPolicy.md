---
type: Workflow
title: "Create DLP Policy"
description: "Describe a new DLP policy as a spec, plan it read-only, show the plan, and — only on the user's explicit yes, with writes enabled by the operator — create it in simulation mode."
tags: [purview, dlp, data-loss-prevention, write]
timestamp: 2026-09-24T00:00:00Z
---

# Create DLP Policy

> One reusable path for any new DLP policy — a merge of old templates, or a new one from a list of
> data types. The policy is a **spec**, not code. Plan first (read-only), create second (a tenant
> write, confirm-gated, simulation mode only).

## What it can and cannot do

- **Can:** create a **new** policy with rules whose data types are copied from existing policies
  (each type keeps its own count and confidence) and/or listed directly; locations Exchange,
  SharePoint, OneDrive, Teams, Devices (each "All"); actions from a closed menu — endpoint
  audit / block with override / block, block access, admin alert.
- **Cannot:** change, switch on, or delete any existing policy or rule; create a policy in any mode
  other than simulation. Switching on is done in the portal (or a later tool, its own yes).

## Steps

1. **Name the tenant.** `gateway://session`. Every message about the plan names it.
2. **Write the spec with the user.** Plain words first ("merge the two EU policies into one rule, 50+
   items, record only"), then the spec (names invented — Contoso):
   ```json
   {
     "name": "Contoso personal data",
     "mode": "simulation",
     "locations": ["exchange", "sharepoint", "onedrive", "devices"],
     "rules": [
       { "name": "EU personal data (50+)", "severity": "High",
         "from_policies": ["Contoso EU policy A", "Contoso EU policy B"] },
       { "name": "Financial data (10+)", "severity": "High",
         "from_policies": ["Contoso finance policy"] }
     ]
   }
   ```
   Defaults: `mode` simulation, `endpoint` audit, `block_access` false, `alert` false. Listed types:
   `"explicit_types": [{ "name": "Credit Card Number", "min_count": 10, "confidence": "high" }]`.
3. **Plan.** `purview.plan_dlp_policy` with the spec → job id. Poll `purview.dlp_job_status` until
   `completed`. It shows the plan in plain words and a `plan_id`. Problems (name taken, unknown
   source or type, over 100 KB) come back all at once — fix the spec and plan again.
   The job signs in to Security & Compliance itself if needed (browser). Needs a role that reads DLP.
4. **Show the user the plan** — every rule, its sources, type count, thresholds, actions, and the
   "not carried over" list. A plan is valid for 24 hours and is refused if changed on disk.
5. **Stop for the operator's role.** The Purview role **DLP Compliance Management** (or Compliance
   Administrator) — theirs (auth-ops), never the agent's; then reconnect so the next job signs in fresh.
6. **Dry run.** `purview.check_dlp_policy_plan` with the `plan_id` (no writes needed) → poll
   `dlp_job_status`. It checks, in the tenant: the tenant, that the role can create, that the name is
   still free, the 600-rule limit, and every parameter — then stops before the first create command.
   A failure names what to fix. It cannot prove Microsoft accepts each rule; only creating does.
   (`-WhatIf` is not used: Microsoft documents that it does not work in Security & Compliance.)
7. **Stop for writes.** `enableWrites: true` for purview in *their* `settings.yaml`, gateway restart,
   `/mcp` reconnect. Without writes, `create_dlp_policy` is not even registered.
8. **Preview.** `purview.create_dlp_policy` with `plan_id` and **no** `confirm` → the preview, with the
   plan in plain words. Show it. Ask: "Create this policy in <tenant>, in simulation mode?"
9. **Create — the person approves in the client.** Call `create_dlp_policy` with `confirm: true`
   and a `reason`. The gateway shows the person the preview as an approval prompt; it runs only if
   they tick *approve* and accept. Declined → stop, do not retry. If the client cannot show the
   prompt (the refusal says so; `gateway.check_approval_prompt` tests it), the operator types instead:
   ```
   ! bun run cli purview dlp create <plan-id> --confirm "<exact policy name>"
   ```
   Without `--confirm` it only shows the plan; a name that does not match is refused. It goes
   through the same guardrail and audit log as the MCP tool. On success it names the policy and
   rules; if a rule failed, it says whether the half-made policy was removed.
10. **Hand back.** Remind the operator to turn writes off again. Next: let the simulation run
   (Activity explorer, Policy mode = Test; or `start_dlp_export` + `analyze_dlp_policies`).

## Gotchas

- **Plan ≠ dry run ≠ create.** `plan_dlp_policy` reads; `check_dlp_policy_plan` connects with the
  create commands loaded but stops before calling them (a test pins that order in the script);
  `create_dlp_policy` is the only Purview tenant write. A "yes" in chat is not the approval — the
  person's click in the client prompt is. Never run the CLI's `--confirm` for them.
- **One PowerShell session at a time.** An export, plan and create share one job slot; a second
  start returns the running job. A gateway restart forgets running jobs.
- **Merging turns "all of" into "any of".** A source rule that needed several types together, or had
  other conditions (shared outside, labels), is listed under "not carried over" — read it out.
- **SharePoint/OneDrive simulation also scans existing files**, so the new policy shows more matches
  there than the old ones did. That is expected, not a difference in coverage.
