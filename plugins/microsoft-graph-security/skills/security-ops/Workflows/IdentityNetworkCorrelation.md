---
type: Workflow
title: "Identity-Side Anomaly Package (for Network Correlation)"
description: "Produce the identity half of an identity+network correlation: SP/user anomaly evidence packaged for an external API gateway or SIEM operator. Executable version of operational flow 10 (identity side only)."
tags: [security-ops, entra, defender, siem, correlation]
timestamp: 2026-07-04T00:00:00Z
---

# Identity-Side Anomaly Package

Source flow: `docs/operational-flows/10-data-leakage-risk-assessment.md`

> The external half of this flow (querying an API gateway / Istio mesh for network-level logs) has **no tools in this stack** — the deliverable here is a complete, correlation-ready identity evidence package for the operator or SIEM that does.

## Steps

1. **Anchor the anomaly.** `defender.list_security_alerts` / `defender.get_security_incident` for the flagged principal; `entra.get_service_principal` or `entra.get_user` to fix the identity (objectId, appId, UPN).
2. **Build the identity timeline.**
   - `entra.list_sign_ins` (bounded window): timestamps, IPs, locations, resources, risk states.
   - `entra.list_directory_audits`: permission/credential/membership changes around the anomaly.
3. **Enumerate what the identity can reach.** Granted app roles (`entra.get_service_principal`) or group/role memberships (`entra.list_user_transitive_member_of`, `entra.list_role_assignments`) — the identity-side blast-radius list the network side should watch.
4. **Package for correlation.** One structured summary: identity, timeline (ISO timestamps + IPs for join keys), reachable resources, defender alert ids. Hand to the operator/SIEM for the network-side join.
5. **Follow-through.** If the correlated verdict comes back malicious, route to `ServicePrincipalContainment.md` (SP) or `SpearphishBlastRadius.md` step 6 (user) for the containment sequence.

## Capability boundaries

- **No external gateway/mesh connectors and no Sentinel MCP yet** (Sentinel is Phase 1 roadmap). This workflow deliberately covers only the identity half; timestamps and IPs are formatted as join keys so the network side can correlate mechanically.
