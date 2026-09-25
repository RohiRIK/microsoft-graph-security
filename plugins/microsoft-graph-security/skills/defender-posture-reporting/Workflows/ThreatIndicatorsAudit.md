---
type: Workflow
title: "Threat Intelligence Indicators & Alert Correlation"
description: "Audit ingested threat intelligence indicators alongside active high-severity alerts to evaluate external threat exposure."
tags: [defender, indicators, alerts, threat-intel]
timestamp: 2026-09-10T12:00:00Z
---

# Threat Intelligence Indicators & Alert Correlation

Source: Defender MCP Threat Audit Engine

> Detailed inspection of threat intelligence indicators ingested into Microsoft Defender correlated with live high-severity detections.

## Steps

1. **Execute Threat Audit.**
   - Call `defender.audit_threat_indicators` (options: `topIndicators`, `topAlerts`).
   - Root CLI shortcut: `bun run cli defender indicators audit --top-indicators 50 --top-alerts 20`.
2. **Review Ingested Threat Intelligence.**
   - Total indicators ingested across the tenant.
   - Categorize by threat type (e.g. malicious IP, domain, URL, file hash) and target product.
   - Note configured actions (`alertAndBlock`, `alert`, `allow`).
3. **Correlate with Active Alerts.**
   - Inspect `findings.highSeverityAlerts`: title, status, severity, created timestamp.
   - Identify if live alerts match known indicator categories or campaigns.
4. **Report & Containment Recommendations.**
   - Emit executive breakdown of active IOC counts and urgent alerts.
   - If malicious files or hosts are confirmed active: hand off to `security-ops` (`SpearphishBlastRadius.md` / `defender.isolate_device` / `defender.block_file_indicator`).

## Capability boundaries

- `audit_threat_indicators` is read-only. Submitting new blocking indicators (`alertAndBlock`) requires `defender.block_file_indicator` (write_critical, confirm: true) with `DEFENDER_ENABLE_WRITES=true`.
