---
name: app-governance
description: Inventories enterprise applications, evaluates permission risk, calculates blast radius scores, audits unscoped mail/SharePoint grants and standing PIM role eligibilities, and executes confirm-gated application containment. USE WHEN asked 'audit our app registrations', 'check high risk apps', 'who has tenant-wide mail access', 'audit Sites.Selected', 'check dormant PIM roles', or 'disable this compromised app'. NOT FOR user offboarding (use security-ops's HostileOffboarding) or single user access reviews (use EntraIdOps).
metadata:
  category: workflow
  effort: medium
  tags: entra, exchange, purview, app-governance, blast-radius, permissions, security
---

# app-governance

End-to-end operational playbook for governing Microsoft Entra ID applications, third-party service principals, high-privilege Graph permissions, resource-scoped delegations (`Mail.*`, `Sites.Selected`), standing PIM role eligibilities, and emergency service principal containment.

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **AppSecurityAudit** | "audit our app registrations", "check app credentials", "stale applications", "blast radius score" | `Workflows/AppSecurityAudit.md` |
| **ResourceAccessReview** | "unscoped mail access", "who can read all mailboxes", "audit Sites.Selected", "check dormant PIM roles" | `Workflows/ResourceAccessReview.md` |
| **ServicePrincipalContainment** | "disable compromised app", "lock down service principal", "contain rogue application" | `Workflows/ServicePrincipalContainment.md` |

## Ground Rules

1. **Always name the tenant first**: Query `gateway://session` or `gateway.whoami` and state the tenant display name and ID before displaying findings.
2. **Blast Radius is a structured risk calculation (0–100)**: Evaluated from application permissions (e.g. `Directory.ReadWrite.All`, `RoleManagement.ReadWrite.Directory`), directory roles held by the service principal, and credential security.
3. **Unscoped Mail vs Application Access Policy**: Graph API permissions like `Mail.Read` or `Mail.ReadWrite` assigned as Application permissions grant access to *all* mailboxes across the organization unless restricted by Exchange Application Access Policies. Always audit these via `exchange.audit_unscoped_mail_access`.
4. **Writes require two-phase confirmation**: Disabling an application (`entra.disable_application`) is `write_destructive`. First call without `confirm` returns a structured preview (affected service principal, current status, prospective change). The user must explicitly approve before calling with `confirm: true`.

## Gotchas

- **App Registration vs Service Principal**: An app registration is the global blueprint; the service principal (`/servicePrincipals`) is the local instantiation holding permissions and role assignments in the client tenant. Blast radius and containment actions target the service principal ID or App ID.
- **Sites.Selected Requires Explicit Site Permissions**: An application with `Sites.Selected` has zero access to SharePoint until granted permissions on specific site collections via `/sites/{id}/permissions`. Use `purview.audit_sites_selected` to audit granted site permissions.
- **PIM Eligibility Age vs Activation**: Standing eligibility (`roleEligibilitySchedules`) represents potential privilege that can be activated on demand. Eligibilities standing longer than 90 days without periodic access reviews represent latent blast radius.

## Examples

**Example 1: App Security & Credential Hygiene Sweep**
```
User: "Audit our enterprise applications for high-risk permissions and expired secrets"
→ AppSecurityAudit → entra.audit_app_registrations(limit: 50, dormant_days: 90)
→ Computes blast radius on flagged apps with entra.get_app_blast_radius(id: app_id)
→ Reports high-risk apps, expiring certs, and recommended containment steps
```

**Example 2: Contain a Malicious or Compromised App**
```
User: "Disable service principal <service-principal-id> immediately"
→ ServicePrincipalContainment → entra.disable_application(id: "...", dry_run: true)
→ Displays impact preview to operator and requests verbal confirmation
→ Upon confirmation, calls entra.disable_application(id: "...", confirm: true)
```
