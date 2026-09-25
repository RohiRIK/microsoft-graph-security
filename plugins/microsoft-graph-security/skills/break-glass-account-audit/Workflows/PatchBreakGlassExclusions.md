# Workflow: PatchBreakGlassExclusions

Safely patch designated emergency-access / break-glass accounts into Conditional Access policy exclusions using two-phase human-in-the-loop confirmation.

## When to Use
- Remediating policies flagged with exclusion gaps during `VerifyBreakGlassCoverage`.
- Preparing a tenant for broad MFA enforcement without risk of administrative lockout.
- "Add our break-glass accounts to all CA policies".

## Ground Rules
1. **Requires ENTRA_ENABLE_WRITES=true**: Modifying policy exclusions is `write_critical`.
2. **Two-phase confirmation**: First call must run without `confirm: true` or with `dry_run: true` to generate a structured preview showing:
   - Target policies evaluated.
   - Policies currently missing the emergency accounts.
   - Proposed updated exclusion array (`conditions.users.excludeUsers`).
3. **Explicit confirmation required**: The operator must verbally review and approve the prospective changes before applying `confirm: true`.

## Steps

1. **Confirm Emergency Account Object IDs**
   Verify the user principal names and object IDs of designated emergency accounts with the operator.

2. **Phase 1: Dry-Run Assessment**
   Call `entra.patch_breakglass_exclusions`:
   ```json
   {
     "breakglass_user_ids": ["<user-id-1>", "<user-id-2>"],
     "dry_run": true,
     "confirm": false
   }
   ```
   If targeting a specific policy rather than all policies, supply `"policy_id": "<policy-id>"`.

3. **Present Preview to Operator**
   Show the operator:
   - Total policies inspected.
   - Policies already protected.
   - Policies requiring updates and their merged exclusion list.

4. **Phase 2: Confirmed Execution**
   Upon explicit verbal sign-off from the operator:
   ```json
   {
     "breakglass_user_ids": ["<user-id-1>", "<user-id-2>"],
     "dry_run": false,
     "confirm": true
   }
   ```
   Verify all target policies report successful patching.
