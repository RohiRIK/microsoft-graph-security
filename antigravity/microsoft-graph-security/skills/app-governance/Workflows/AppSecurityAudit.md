# Workflow: AppSecurityAudit

Audit application registrations and service principals in the tenant for privilege creep, high-risk application permissions, stale or dormant applications, and expired or expiring credentials.

## When to Use
- Periodic application governance sweeps.
- "Audit our apps", "check app credentials", "stale applications".
- Assessing blast radius of an existing enterprise app or service principal.

## Steps

1. **Verify Session & Tenant Context**
   Call `gateway.whoami` or inspect `gateway://session`. State tenant display name and GUID.

2. **Audit Applications for Privilege & Credential Hygiene**
   Call `entra.audit_app_registrations`:
   ```json
   {
     "limit": 50,
     "dormant_days": 90
   }
   ```
   Inspect results:
   - Apps flagged with `HIGH_PRIVILEGE_PERMISSIONS` (e.g. `RoleManagement.*`, `Directory.ReadWrite.All`, `AppRoleAssignment.*`).
   - Apps flagged with `EXPIRED_CREDENTIALS` or `EXPIRING_CREDENTIALS`.
   - Stale apps with no sign-in or creation older than threshold days (`dormant_days`).

3. **Calculate Blast Radius for Elevated Applications**
   For any application holding High risk permissions or directory roles, call `entra.get_app_blast_radius`:
   ```json
   {
     "id": "<service-principal-id-or-app-id>"
   }
   ```
   Review:
   - `blastRadiusScore` (0–100 scale: Low, Medium, High, Critical).
   - Assigned directory roles (e.g. Global Administrator, Application Administrator).
   - High-privilege Graph application scopes.

4. **Formulate Report & Recommendations**
   - Present findings table with Application Name, App ID, Overall Risk, Key Findings, and Blast Radius Score.
   - For applications with expired credentials or critical blast radius that are dormant, recommend disabling via `ServicePrincipalContainment`.
