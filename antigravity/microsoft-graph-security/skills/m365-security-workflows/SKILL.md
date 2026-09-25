---
name: m365-security-workflows
description: Routes Microsoft 365 security, identity, device, mail, compliance, triage, and operational requests to the repository's canonical cloud-security-engineer, security-ops, and supporting skills. USE WHEN investigating a tenant, triaging a user or device, checking posture, or planning a confirm-gated response. NOT FOR single-plane lookups that the named backend skill handles directly.
metadata:
  category: workflow
  effort: medium
---

# Microsoft 365 security workflows

This is the portable entry point. Load the canonical repository skill for the requested scenario; do not copy or improvise its procedures here.

## Routing

- Cross-plane investigation, tenant posture, risky sign-ins, MFA, privilege, offboarding, exfiltration, insider risk, or legal-hold gaps: load the `cloud-security-engineer` skill.
- Operational response, JIT access, access denied, compliance remediation, phishing purge, hostile offboarding, spearphish blast radius, or service-principal containment: load the `security-ops` skill.
- Gateway setup or startup: load the `gateway-bootstrap` skill.
- Authentication, tenants, scopes, consent, or credentials: load the `auth-ops` skill.
- Intune configuration drift: load the `analyze-configuration` skill.
- Application governance: load the `app-governance` skill.
- Purview operations: load the `purview-compliance-ops` skill.
- Defender posture: load the `defender-posture-reporting` skill.
- Session hygiene: load the `session-hygiene-audit` skill.
- Gateway disconnect or read-only verification: load the `gateway-disconnect-check` skill.

Read `references/runtime-and-safety.md` before using a host adapter. The host adapter only selects the MCP entry point; the canonical skill owns the workflow and safety rules.

## Non-negotiable safety

- Name the tenant from `gateway://session` in the opening line. Never invent a tenant, user, profile, or result.
- Read-only by default. Writes require both the package write opt-in and `confirm: true` at call time; destructive and critical writes require an explicit human approval preview first.
- Never print tokens, secrets, or unmasked personal data. Keep configuration and credentials outside the plugin.
- If a plane is unavailable or returns 403, state the missing evidence and continue only with the data actually returned.
- Do not choose or switch a client tenant, grant consent, enable writes, or perform an external action for the user.
