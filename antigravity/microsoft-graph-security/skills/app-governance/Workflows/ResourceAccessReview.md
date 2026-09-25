# Workflow: ResourceAccessReview

Audit resource-scoped delegations and privileges across Exchange Online mailboxes, SharePoint site collections, and standing PIM directory role eligibilities.

## When to Use
- "Who has unscoped access to mailboxes?"
- "Check SharePoint Sites.Selected applications"
- "Audit standing PIM role assignments"
- Periodic resource delegation reviews.

## Steps

1. **Verify Session & Tenant Context**
   Call `gateway.whoami` or inspect `gateway://session`. Open findings with tenant display name and GUID.

2. **Audit Unscoped Mail Access**
   Enterprise applications holding `Mail.Read`, `Mail.ReadWrite`, or `Mail.Send` application permissions have tenant-wide access to all organization mailboxes unless constrained by Exchange Application Access Policies (`New-ApplicationAccessPolicy`).
   Call `exchange.audit_unscoped_mail_access`:
   ```json
   {
     "limit": 50
   }
   ```
   Examine any apps holding broad `Mail.*` permissions and flag their risk level (`Critical` for ReadWrite/Send, `High` for Read).

3. **Audit SharePoint `Sites.Selected` Delegations**
   For sensitive SharePoint site collections, verify which applications have been explicitly granted read/write permissions under the `Sites.Selected` model.
   Call `purview.audit_sites_selected`:
   ```json
   {
     "site_id": "<site-id-or-composite-web-url>"
   }
   ```
   Inspect `applicationGrants` to verify only authorized backup, governance, or archiving applications hold access.

4. **Audit Standing PIM Directory Role Eligibilities**
   Eligible role assignments that sit dormant without regular activation or access reviews increase attack surface.
   Call `entra.audit_dormant_pim_eligibility`:
   ```json
   {
     "threshold_days": 90,
     "top": 50
   }
   ```
   Filter and highlight:
   - Standing eligibilities for high-privilege roles (`Global Administrator`, `Privileged Role Administrator`, etc.) standing `>= 90 days`.
   - Permanent eligibilities (`isPermanent: true`, no expiration).

5. **Summarize Review Findings**
   Synthesize the resource access posture into an executive summary table detailing:
   - Applications with unconstrained mailbox access.
   - Applications with site-specific SharePoint access.
   - Users/Principals with long-standing dormant PIM eligibilities.
