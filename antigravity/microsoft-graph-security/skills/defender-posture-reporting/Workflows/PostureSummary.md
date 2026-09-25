---
type: Workflow
title: "Security Posture Summary"
description: "Secure score trend + top control gaps + ingested threat indicator volume, as an executive-readable summary."
tags: [defender, secure-score, reporting]
timestamp: 2026-07-31T00:00:00Z
---

# Posture Summary

## Steps

1. `defender.list_secure_scores` — pull the recent time series (not just latest); compute trend direction.
2. `defender.list_secure_score_control_profiles` — filter to controls with meaningful point value not yet implemented; drop license-gated/not-implementable controls from the "actionable" list but still mention count.
3. `defender.audit_threat_indicators` (or CLI `bun run cli defender indicators audit`) — correlates total ingested IOCs and threat types with active high-severity alerts.
4. Optionally, `defender.list_security_incidents` for a headline count of open incidents (context, not the focus of this report — deep incident work belongs to `security-ops`).
5. **Compose the summary**: current score + trend, top 3-5 actionable control gaps by point value, IOC ingestion volume and active alert correlation, open incident count. Written for a non-technical stakeholder — translate control names into plain-language risk statements.

## Gotchas

- Don't report a raw list of every control profile — that's a portal dump, not a summary. Rank by point value and cap at the top few.
- If `list_secure_scores` returns only a single data point (new tenant, no history), say so explicitly rather than fabricating a trend.
