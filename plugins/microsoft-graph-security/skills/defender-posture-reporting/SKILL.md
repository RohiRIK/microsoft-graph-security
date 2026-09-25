---
name: defender-posture-reporting
description: Turn defender_mcp's secure score, control profile, and threat indicator tools into a posture summary for leadership or a client review. USE WHEN asked for a security posture report, secure score trend, 'what's our Defender score', or a summary of active threat indicators. NOT FOR live incident triage (use security-ops's SpearphishBlastRadius/ServicePrincipalContainment, which treat Defender as an evidence source) or cross-plane anomaly correlation (use cloud-security-engineer).
metadata:
  category: workflow
  effort: medium
  tags: defender, secure-score, posture, reporting
---

# defender-posture-reporting

This skill uses only `defender_mcp`'s read tools. (`DEFENDER_ENABLE_WRITES=true` registers two `write_critical`
tools, `block_file_indicator` and `isolate_device`; this skill never calls them.) This skill
surfaces secure scores, control profiles, and threat intelligence audits for periodic posture reports,
leadership reviews, and client QBRs.

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **PostureSummary** | "secure score report", "posture summary", "how are we doing security-wise" | `Workflows/PostureSummary.md` |
| **ThreatIndicatorsAudit** | "audit threat indicators", "threat intel sweep", "correlate IOCs and alerts" | `Workflows/ThreatIndicatorsAudit.md` |

## Ground Rules

1. **Secure score alone is a vanity metric** — always pair it with `list_secure_score_control_profiles` to name the specific unimplemented controls driving the gap, not just the number.
2. **Threat indicators correlate with live detections** — use `defender.audit_threat_indicators` (or CLI `bun run cli defender indicators audit`) to inspect ingested IOCs alongside active high-severity alerts.
3. Delegated interactive sign-in (`DEFENDER_CLIENT_ID=wellknown`) is the default, with `app_only` fully supported. Defender for Endpoint machine tools require `app_only`.

## Gotchas

- `list_secure_scores` returns a time series, not a single number — report the trend (improving/flat/declining) alongside the latest value, not just the latest snapshot.
- A control profile marked "not implementable" for this tenant's licensing tier still counts against the score visually in the portal but shouldn't be reported as an actionable gap — filter these out or label them clearly as license-gated.

## Examples

**Example 1: Monthly client posture report**
```
User: "Give me this month's security posture summary for the client review"
→ PostureSummary → list_secure_scores (trend) + list_secure_score_control_profiles (gaps)
→ list_threat_indicators (ingested IOC count) → summarized as a report, not raw dumps
```
