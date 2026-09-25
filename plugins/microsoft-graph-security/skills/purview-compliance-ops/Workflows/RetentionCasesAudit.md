---
type: Workflow
title: "Compliance Retention & Legal Hold Audit"
description: "Audit active eDiscovery cases, active legal holds, and published retention labels across Microsoft Purview."
tags: [purview, retention, ediscovery, legal-hold, audit]
timestamp: 2026-09-10T12:00:00Z
---

# Compliance Retention & Legal Hold Audit

Source: Purview MCP Retention Audit Engine

> Holistic compliance audit evaluating active eDiscovery matters, active custodian legal holds, and published data retention policies.

## Steps

1. **Execute Retention & Cases Audit.**
   - Call `purview.audit_retention_cases` (options: `topCases`, `topLabels`).
   - Root CLI shortcut: `bun run cli purview cases audit`.
2. **Review Active Cases & Legal Holds.**
   - Total eDiscovery cases vs active ongoing cases (`status: 'active'`).
   - Identify cases that have active legal holds applied.
   - For cases with holds: review specific case details via `purview.get_ediscovery_case` or custodians via `purview.list_ediscovery_custodians`.
3. **Review Published Retention Labels.**
   - Published retention label definitions, configured retention period behaviors, and actions after expiration (`delete`, `startRetention`, `none`).
   - Note: Retention label query requires delegated access (`RecordsManagement.Read.All`); degrades gracefully under app-only mode.
4. **Identify Gaps & Generate Summary.**
   - Flag any cases with discrepancies or missing custodian coverage.
   - Emit consolidated compliance overview for Legal and Records Management teams.

## Capability boundaries

- `audit_retention_cases` is read-only. Creating, applying, or releasing legal holds and retention labels are manual actions in the Microsoft Purview compliance portal.
