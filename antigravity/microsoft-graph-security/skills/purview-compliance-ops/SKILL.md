---
name: purview-compliance-ops
description: Execute Microsoft Purview compliance workflows (eDiscovery case review, custodian legal-hold coverage, threat assessment triage, DLP policy analysis, creating a new DLP policy in simulation) against purview_mcp via the gateway (purview.*). USE WHEN opening or reviewing an eDiscovery case, checking whether a custodian's legal hold is actually applied, triaging a user-reported phishing/malware submission, analysing DLP policies and their gaps, or creating/merging a DLP policy. NOT FOR cross-plane insider-risk correlation (use cloud-security-engineer's U15/U16 flags) or CA/device policy provisioning (use conditional-access-provisioning / device-compliance-baseline-provisioning).
metadata:
  category: workflow
  effort: medium
  tags: purview, ediscovery, legal-hold, compliance, retention, threat-assessment, dlp
---

# purview-compliance-ops

`purview_mcp` (`purview.*` through the gateway) is a read-only compliance plane with **one** write:
`create_dlp_policy`, registered only when the operator enables writes, and only able to create a
*new* DLP policy in simulation mode (`Workflows/CreateDlpPolicy.md`). Everything else ends in a
**finding**, not an action: legal hold enforcement, case disposition, and threat-assessment response
happen in the Purview/Defender portals by a human; this skill only gets you the evidence.

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **RetentionCasesAudit** | "audit retention and cases", "retention overview", "active holds overview" | `Workflows/RetentionCasesAudit.md` |
| **EdiscoveryCaseReview** | "review this eDiscovery case", "who's on legal hold for X", "case status" | `Workflows/EdiscoveryCaseReview.md` |
| **LegalHoldCoverageCheck** | "is this custodian on hold", "hold gap", "released while case still open" | `Workflows/LegalHoldCoverageCheck.md` |
| **ThreatAssessmentTriage** | "phishing submission", "malware report", "threat assessment status" | `Workflows/ThreatAssessmentTriage.md` |
| **DlpPolicyAnalysis** | "analyse our DLP policies", "DLP gaps", "which DLP rules do nothing", "is DLP working" | `Workflows/DlpPolicyAnalysis.md` |
| **CompareDlpPolicies** | "is the merged policy ready", "compare the new DLP policy with the old ones", "can we switch it on" | `Workflows/CompareDlpPolicies.md` |
| **CreateDlpPolicy** | "create a DLP policy", "merge these DLP policies", "build the consolidated policy" | `Workflows/CreateDlpPolicy.md` |

## Ground Rules

1. **`list_retention_labels`/`get_retention_label` are delegated-only.** `RecordsManagement.Read.All` has no application-permission equivalent — under the default `app_only` access mode these two tools are **not registered at all**, not merely denied. A missing tool here is that gating, not an outage; check `purview_mcp`'s access mode before treating it as a bug. `audit_retention_cases` degrades gracefully under `app_only` by returning case summaries with empty labels.
2. **Join on custodian `email` ↔ UPN**, case-insensitive — same join model as `cloud-security-engineer`.
3. **Case status matters more than case existence.** A closed case with an unreleased hold is itself a finding (`HOLD_GAP`), not a null result.

## Quick Reference — tools by task

| Task | Tool |
|------|------|
| Full cases & labels audit | `audit_retention_cases` (CLI: `bun run cli purview cases audit`) |
| List/inspect a case | `list_ediscovery_cases`, `get_ediscovery_case` |
| Who's on hold | `list_ediscovery_custodians` |
| Non-custodial sources (shared mailboxes, sites) | `list_ediscovery_noncustodial_data_sources` |
| Search + review-set state | `list_ediscovery_searches`, `list_ediscovery_review_sets` |
| Phishing/malware submissions | `list_threat_assessment_requests`, `get_threat_assessment_request` |
| Retention label lookup (delegated mode only) | `list_retention_labels`, `get_retention_label` |
| DLP policy analysis | `start_dlp_export` → `dlp_export_status` → `analyze_dlp_policies` (the job signs in itself when needed) |
| New policy vs the ones it replaces | `start_dlp_export` → `compare_dlp_policies` (`plan_id`); report: `purview dlp compare` + `dlp_compare_spec.py` |
| New DLP policy (merge or new) | `plan_dlp_policy` → `check_dlp_policy_plan` (dry run) → `create_dlp_policy` (preview, then `confirm: true` on the user's yes; writes on); `dlp_job_status` after each |

## Gotchas

- Don't assume a custodian's absence from `list_ediscovery_custodians` means no hold — check `list_ediscovery_noncustodial_data_sources` too; shared mailboxes and SharePoint sites are held separately from named custodians.
- Writes cover only `create_dlp_policy` — there is no write path to apply/release a hold, or to change an existing DLP policy; those are manual portal actions, state it explicitly rather than implying the skill did it.
- A `threat_assessment_request` with no resolution after several days is itself worth flagging — don't just report status, note staleness.
- DLP is not in Graph. `start_dlp_export` → `dlp_export_status` → `analyze_dlp_policies`; the job reuses the Security & Compliance sign-in or makes it itself in the browser — see `Workflows/DlpPolicyAnalysis.md`.

## Examples

**Example 1: Legal hold coverage check**
```
User: "Is jsmith@contoso.com actually on hold for the Contoso-v-Acme case?"
→ LegalHoldCoverageCheck → get_ediscovery_case + list_ediscovery_custodians (filter email)
→ Reports hold status; flags HOLD_GAP if case is active and custodian isn't listed
```

**Example 2: Phishing submission triage**
```
User: "What's the status on the phishing report from accounting?"
→ ThreatAssessmentTriage → list_threat_assessment_requests → get_threat_assessment_request
→ Reports category, verdict, and days-open; recommends escalation if stale
```
