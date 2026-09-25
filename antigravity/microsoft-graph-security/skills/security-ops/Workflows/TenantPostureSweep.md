---
type: Workflow
title: "Cross-Plane Tenant Security Posture Sweep"
description: "Comprehensive security scorecard evaluating Entra app credentials, Defender alerts/indicators, Intune firewall policies, Exchange forwarding rules, and Purview retention/legal holds."
tags: [security-ops, posture, cross-plane, triage, scorecard]
timestamp: 2026-09-10T12:00:00Z
---

# Cross-Plane Tenant Security Posture Sweep

Source: Unified Cross-Plane Triage CLI & Graph MCP Suite Modernization

> Routine or incident-driven tenant posture scorecard evaluating exposure, credential hygiene, endpoint protection, and exfiltration vectors across all 5 Graph planes.

## Steps

1. **Execute Root Triage Scorecard.**
   - Run `bun run cli triage posture` (or with `--markdown` for formatted output).
   - Alternatively, invoke individual tools in parallel through the gateway:
     - `entra.audit_credential_hygiene`: Expired/expiring application secrets & certificates.
     - `defender.audit_threat_indicators`: Active high-severity alerts correlated with ingested threat intelligence.
     - `intune.audit_firewall_policies`: Windows Firewall endpoint security policies and classic profile drift.
     - `exchange.audit_forwarding_rules`: Suspicious mailbox forwarding, redirect, and auto-delete rules.
     - `purview.audit_retention_cases`: Active eDiscovery cases and published retention labels.
2. **Evaluate Overall Rating & Priority Actions.**
   - **`CRITICAL_RISK`**: Triggered by expired enterprise credentials, active high-severity Defender alerts, zero Intune firewall policies, or detected mailbox forwarding/auto-deletion rules.
   - **`NEEDS_ATTENTION`**: Triggered by credentials expiring within 30 days or legacy classic firewall profiles.
   - **`HEALTHY`**: Clean baseline across all evaluated planes.
3. **Dispatch Targeted Remediation Workflows.**
   - **Expired Credentials**: Dispatch `AppSecretExpiryTriage.md` or run `bun run cli entra apps hygiene`.
   - **Active High-Severity Alerts**: Dispatch `SpearphishBlastRadius.md` or investigate via `bun run cli defender alerts list`.
   - **Firewall Policy Gaps**: Dispatch `ComplianceRemediation.md` or deploy Endpoint Security Firewall policy (`bun run cli intune security firewall`).
   - **Suspicious Mailbox Rules**: Dispatch `SpearphishBlastRadius.md` or audit via `bun run cli exchange mail forwarding`.
   - **eDiscovery / Hold Oversight**: Dispatch `purview-compliance-ops` or review via `bun run cli purview cases audit`.
4. **Report & Executive Summary.**
   - Emit consolidated markdown scorecard with object GUIDs, counts, and assigned remediation owners.

## Flag rules in play

- **HYGIENE_RISK** / **EXPIRED_CRED** — Expired or soon-to-expire app credentials.
- **THREAT_ALERT** — Active high-severity alerts in Defender.
- **FIREWALL_GAP** — Zero Windows Firewall policies active in Intune.
- **CLASSIC_PROFILE** — Legacy classic firewall profile requiring migration.
- **BEC_FORWARDING** — Unauthorized external forwarding or auto-deletion rules.

## Capability boundaries

- **Triage is read-only:** `triage posture` is an analytical scorecard. Remediations (rotating secrets, updating policies, isolating devices) follow the explicit confirm-gated write workflows of each respective plane.
