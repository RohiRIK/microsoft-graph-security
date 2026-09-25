---
type: Workflow
title: "DLP Policy Analysis"
description: "Inventory the tenant's Microsoft Purview DLP policies, find enforcement gaps, and measure 30-day effectiveness from a local snapshot."
tags: [purview, dlp, data-loss-prevention, audit]
timestamp: 2026-09-23T00:00:00Z
---

# DLP Policy Analysis

> What DLP policies exist, what they actually protect, where the gaps are, and which ones are dead
> weight. Read-only. Design and evidence: `docs/plans/dlp-policy-analysis.md`.

DLP configuration is **not in Microsoft Graph**. It is exported through Security & Compliance
PowerShell into a per-tenant snapshot — by an MCP background job — and analysed from the snapshot.

## Steps

1. **Name the tenant first.** Read `gateway://session` (or `gateway.whoami`). The report opens with it.
2. **Check for a snapshot.** Call `purview.analyze_dlp_policies`. If it answers "No DLP snapshot for
   this tenant yet", or the snapshot is older than the question needs, go to step 3; otherwise step 4.
3. **Export.** `purview.start_dlp_export` (`days` 1–30) returns a job id at once; poll
   `purview.dlp_export_status` until `completed` (a 30-day export can take 20+ minutes — progress
   shows one line per day). With no current Security & Compliance sign-in the job opens the
   Microsoft sign-in in the browser first — the operator answers it; the reply says so.
   Needs `pwsh` 7 + ExchangeOnlineManagement ≥ 3.2 and a Purview role that reads DLP (**View-Only DLP
   Compliance Management**). Without the MCP: `bun run cli purview dlp export`.
4. **Analyse.** `purview.analyze_dlp_policies` (`min_severity` to trim, `snapshot_id` for an older
   one). CLI: `bun run cli purview dlp analyze --format markdown`.
5. **Report**, most severe first. For each finding say what it means for this tenant and the portal
   change that would close it — this skill changes nothing itself.

## Reading the flags

| Flag | Meaning | Usual fix (portal, by a human) |
|---|---|---|
| `DLP_NOT_ENFORCED` | Policy in simulation or disabled | Review simulation results, then turn it on |
| `DLP_NO_ACTION` | Rule records matches, does nothing a person would notice | Add block / notify / alert, or delete the rule |
| `DLP_AUDIT_ONLY_ENDPOINT` | Every device restriction is Audit | Move the riskiest (removable media, cloud egress) to Block or Warn |
| `DLP_COVERAGE_GAP` | No enforced policy on a workload | Only a gap if the tenant is licensed for that workload |
| `DLP_BROAD_EXCLUSION` | Users, groups or sites excluded | Confirm each exclusion is still justified |
| `DLP_WEAK_THRESHOLD` | One low-confidence hit triggers, or a high count with nothing catching fewer | Tune confidence or add a low-volume rule |
| `DLP_OVERRIDE_UNCHECKED` | Override without justification, or unrecorded | Require justification; alert on overrides |
| `DLP_NO_ALERTING` | High-severity block with no alert or incident report | Turn on alerts |
| `DLP_OVERLAP` | Several policies act differently on the same type and workload | Confirm the layering is intended — strictest wins |
| `DLP_NOT_DISTRIBUTED` | Policy not distributed to its locations | Check policy sync in the portal |
| `DLP_NEVER_FIRES` | No matches in the window | Scoped to nothing, or the condition never occurs |
| `DLP_NOISY` | One rule produces most matches | Likely false positives — tune |
| `DLP_HIGH_OVERRIDE` | Users override a block often | The control is not holding |
| `DLP_SIMULATION_WOULD_BLOCK` | Test-mode policy matching real traffic | Evidence for enabling it |

## Gotchas

- **A DLP job may open a browser sign-in** (only a job; status never does). It reuses a current
  Exchange Online PowerShell sign-in, else signs in first. Do not route it through the Graph
  sign-in — Security & Compliance refuses that token (`UnAuthorized`).
- **A reconnect forgets a running export.** Jobs live in the purview server process; `/mcp` restarts
  it. Start again rather than waiting on a job id that no longer exists.
- **`effectiveness: partial` or `unavailable` is not "never fires".** A failed match export skips
  the effectiveness checks and says why in `notes`. Report it as missing data, not as a finding.
- **Coverage gaps are not licence-aware.** A workload the tenant is not licensed for shows as a gap;
  say so rather than recommending a policy for it.
- **The snapshot holds counts, not people.** User, file, IP and device are dropped inside the export
  script. To investigate one user's DLP matches, use Activity Explorer in the portal.
