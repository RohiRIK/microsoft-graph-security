# Workflow: ServicePrincipalContainment

Safely disable and contain a compromised, unauthorized, or high-risk enterprise application service principal using two-phase human-in-the-loop confirmation.

## When to Use
- Compromised application credentials or detected anomaly in service principal sign-in.
- Offboarding an unapproved or deprecated third-party integration.
- Immediate incident response against a malicious OAuth app.

## Ground Rules
1. **Never disable without previewing impact**: Always run with `dry_run: true` or without `confirm: true` first to retrieve the current state and affected entity details.
2. **Require explicit operator confirmation**: The operator must verbally confirm disabling the target application before executing `confirm: true`.
3. **Fails closed**: Writing requires `ENTRA_ENABLE_WRITES=true`. If writes are not enabled, the tool will refuse execution.

## Steps

1. **Investigate Target Service Principal**
   Retrieve the service principal details and blast radius before containment:
   ```json
   {
     "id": "<service-principal-id>"
   }
   ```
   Call `entra.get_service_principal` and `entra.get_app_blast_radius` to understand current assignments and roles.

2. **Phase 1: Dry-Run / Preview Refusal**
   Execute containment preview:
   ```json
   {
     "id": "<service-principal-id>",
     "dry_run": true,
     "confirm": false
   }
   ```
   Show the returned preview to the operator:
   - Application Display Name and App ID.
   - Current `accountEnabled` status.
   - Proposed change (`accountEnabled: false`).

3. **Phase 2: Confirmed Execution**
   Upon receiving explicit confirmation from the operator:
   ```json
   {
     "id": "<service-principal-id>",
     "dry_run": false,
     "confirm": true
   }
   ```
   Confirm output status reports `{ "disabled": true }`.
