# Cloud Security Engineer — Playbook

Operational detail for all 10 scenarios. Load when a question spans both planes or requires investigation.

## Output Shape

Always, for correlated answers:

```
⚠️ Flags (most severe first)
- CONTRADICTION  <device> — Entra sign-in isCompliant=true vs Intune complianceState=noncompliant (signin 2026-06-30T08:00Z)
- STALE          <device> — compliant but lastSync 12d ago
- ORPHAN         <device> — owner jane@x disabled
- RISKY_SIGNIN   <user>   — high-risk sign-in from 203.0.113.42 (2026-06-30T09:15Z)
- MFA_WEAK       <user>   — privileged user with 3 MFA failures in 24h
- PRIV_RISK      <user>   — Global Admin with noncompliant device
- OFFBOARD_GAP   <device> — orphaned, lastSync 45d ago

Triage table
| user (UPN) | device | OS | compliance (Intune) | CA view (Entra) | lastSync | flags |
```

If there are no flags, say so explicitly (`No contradictions found across 1 device / 3 users.`) — silence is not a pass.

---

## U1 — "who/which users are signed in" (+ their devices)

**Intent:** Correlate recent sign-ins with device compliance posture.

**Procedure:**
1. entra `list_sign_ins` with bounded window (default 24h; `from`/`to` ISO).
2. Distinct users by `userPrincipalName`.
3. Per UPN: intune `search_managed_devices` (prefix on UPN) — user may have 0..n devices.
4. Emit table: UPN · device · OS · Intune compliance · sign-in `deviceDetail.isCompliant` · lastSync. No device → `device: none`.
5. Apply flag rules across each (user, device) pair; flags section first.

**Fields used:**
- Entra: `userPrincipalName`, `deviceDetail.deviceId`, `deviceDetail.isCompliant`, `deviceDetail.operatingSystem`, `createdDateTime`
- Intune: `deviceName`, `operatingSystem`, `complianceState`, `lastSyncDateTime`, `userPrincipalName`

---

## U2 — "is device X really compliant?"

**Intent:** Compare Entra CA view with Intune compliance state for a specific device.

**Procedure:**
1. intune `search_managed_devices` (or `get_managed_device`) → `complianceState`, `lastSyncDateTime`, `userPrincipalName`, `azureADDeviceId`.
2. entra `list_sign_ins` filtered to that user (and where `deviceDetail.deviceId == azureADDeviceId`) → latest `deviceDetail.isCompliant`.
3. Verdict:
   - **AGREE** — both compliant
   - **CONTRADICTION** — differ, name both + timestamps
   - **STALE** — compliant but old sync
   - **UNKNOWN** — no CA device view (missing `deviceDetail`)

**Fields used:**
- Intune: `complianceState`, `lastSyncDateTime`, `azureADDeviceId`, `userPrincipalName`
- Entra: `deviceDetail.isCompliant`, `deviceDetail.deviceId`, `createdDateTime`

---

## U3 — "show false / failed compliance states" (fleet sweep)

**Intent:** Find devices where compliance state is misleading.

**Procedure:**
1. intune `list_managed_devices` (filter `complianceState eq 'compliant'` for false-positive hunt; also pull noncompliant for reverse).
2. For each, resolve owner via entra `get_user`/`search_users` (UPN) → `accountEnabled`.
3. Optionally cross-check recent sign-in `deviceDetail`.
4. Apply all three rules (CONTRADICTION, STALE, ORPHAN); output flags-first, then per-device table.

**Fields used:**
- Intune: `complianceState`, `lastSyncDateTime`, `userPrincipalName`, `managementState`
- Entra: `accountEnabled`, `deviceDetail.isCompliant`

---

## U4 — "triage user U"

**Intent:** Full identity + device + role analysis for a specific user.

**Procedure:**
1. entra `get_user`/`search_users` → `accountEnabled`, ids; `list_role_assignments` (privileged?); `list_sign_ins` for U (recent failures, CA results).
2. intune `search_managed_devices` by UPN → each device's compliance + sync.
3. Lead with any CONTRADICTION/STALE/ORPHAN, then identity summary, then device summary.

**Output:**
```
⚠️ Flags (if any)
Identity Summary
- User: display name (UPN)
- Account: enabled/disabled
- Roles: [list privileged roles]
- Recent sign-ins: N (M failures)
Device Summary
| device | OS | compliance | lastSync | flags |
```

---

## U5 — "risky sign-in triage"

**Intent:** Identify high-risk sign-ins and correlate with device posture.

**Procedure:**
1. entra `list_sign_ins` with filter `riskLevelAggregated ne 'none'` (or inspect returned `riskLevelAggregated` field).
2. Distinct users by UPN.
3. Per UPN: intune `search_managed_devices` → device compliance.
4. Per sign-in: check `status.errorCode`, `conditionalAccessStatus`, `ipAddress`.
5. Flag rules:
   - **RISKY_SIGNIN** — `riskLevelAggregated` in (medium, high) on a managed device
   - **CONTRADICTION** — if device `complianceState` differs from `deviceDetail.isCompliant`
   - **MFA_WEAK** — if sign-in shows MFA failure (`status.errorCode` 500199, 65001)

**Output:**
```
⚠️ Risk Flags
- RISKY_SIGNIN  jsmith@northwind.com — high-risk from 203.0.113.42 (2026-06-30T09:15Z, app: Azure Portal)
- MFA_WEAK      jsmith@northwind.com — MFA failure (error 50199) at 2026-06-30T08:30Z

Risk Detail
| user | risk level | IP | app | CA status | device compliance | flags |
```

**Fields used:**
- Entra: `riskLevelAggregated`, `status.errorCode`, `status.failureReason`, `ipAddress`, `conditionalAccessStatus`, `appDisplayName`
- Intune: `complianceState`, `deviceName`

---

## U6 — "why is device noncompliant?"

**Intent:** Investigate why a device is noncompliant — which policy is failing.

**Procedure:**
1. intune `get_managed_device` → `complianceState`, `complianceGracePeriodExpirationDateTime`.
2. intune `list_device_compliance_policies` → list all policies with `@odata.type`, `version`.
3. For each policy: intune `get_device_compliance_policy` → check settings.
4. intune `list_audit_events` (filter by device name or recent time) → check for configuration changes.
5. intune `list_device_configurations` → check assigned profiles.
6. Correlate: which policy was modified recently? Any audit events showing failures?

**Output:**
```
⚠️ Compliance Failure Analysis
Device: WINDEV2407EVAL
Compliance State: noncompliant
Grace Period Expires: 2026-07-07

Assigned Policies
| policy | type | version | last modified | status |
|--------|------|---------|---------------|--------|
| Windows Encryption | deviceCompliancePolicy | 1 | 2026-06-28 | ⚠️ failing |

Recent Audit Events
| time | activity | result | actor |
|------|----------|--------|-------|

Likely Cause
- Policy "Windows Encryption" requires BitLocker — device shows isEncrypted=false
```

**Fields used:**
- Intune: `complianceState`, `complianceGracePeriodExpirationDateTime`, `isEncrypted`, `lastSyncDateTime`
- Intune: `list_device_compliance_policies`, `get_device_compliance_policy`, `list_audit_events`, `list_device_configurations`

---

## U7 — "phishing investigation"

**Intent:** Investigate a suspected phishing incident — find suspicious sign-ins and correlate with device state.

**Input:** Suspicious URL, email indicator, or user reports suspicious activity.

**Procedure:**
1. entra `list_sign_ins` for the affected user (last 7 days) → look for:
   - Unusual IP addresses
   - Sign-ins to uncommon apps
   - High `riskLevelAggregated`
   - `conditionalAccessStatus` = failure
2. entra `list_directory_audits` for the user (last 7 days) → look for:
   - Password changes
   - Role assignments
   - MFA changes
   - Mail forwarding rules
3. intune `search_managed_devices` → device compliance at time of incident.
4. Correlate timeline: sign-in → suspicious activity → device state.

**Output:**
```
⚠️ Phishing Investigation
User: jsmith@northwind.com
Suspicious Indicator: [URL/email]

Timeline
| time | event | details |
|------|-------|---------|
| 2026-06-30 09:15Z | Sign-in | IP 203.0.113.42, app: M365 Cloud MCP, risk: high |
| 2026-06-30 09:20Z | Password change | Actor: jsmith@northwind.com |
| 2026-06-30 09:25Z | Mail forwarding | Forward to external@attacker.com |

Device State
- Device: WINDEV2407EVAL
- Compliance: compliant
- Last sync: 2026-06-29

Assessment
- High-risk sign-in from unusual IP followed by password change and mail forwarding
- Device appears compliant — possible credential compromise without device compromise
```

**Fields used:**
- Entra: `list_sign_ins` (IP, app, risk, CA status), `list_directory_audits` (operationType, targetResources, initiatedBy)
- Intune: `search_managed_devices` (complianceState, lastSyncDateTime)

---

## U8 — "MFA weakness check"

**Intent:** Identify users with weak MFA posture, especially privileged users.

**Procedure:**
1. entra `list_role_assignments` → identify privileged roles (Global Admin, Privileged Role Admin, etc.).
2. For each privileged user: entra `list_sign_ins` (last 7 days) → check for:
   - MFA failures (`status.errorCode` 500199, 65001)
   - `conditionalAccessStatus` = failure
   - `riskLevelAggregated` ≠ none
3. entra `get_user` → check `strongAuthenticationRequirements` (if available).
4. Flag: **MFA_WEAK** — privileged user with MFA failures or high risk.

**Output:**
```
⚠️ MFA Weakness Report
Privileged Users: 2
Users with MFA Issues: 1

| user | roles | MFA failures (7d) | risk level | last sign-in | flags |
|------|-------|-------------------|------------|--------------|-------|

Recommendations
- jsmith@northwind.com: 3 MFA failures in 24h — review authentication methods
```

**Fields used:**
- Entra: `list_role_assignments` (roleDefinition.displayName), `list_sign_ins` (status.errorCode, riskLevelAggregated), `get_user`

---

## U9 — "privilege escalation detection"

**Intent:** Detect recent privilege escalations and check if newly privileged users have compliant devices.

**Procedure:**
1. entra `list_directory_audits` (last 7 days) → filter `operationType eq 'Add member to role'`.
2. For each role assignment: entra `get_user` → check `accountEnabled`.
3. intune `search_managed_devices` → check device compliance for newly privileged users.
4. Flag: **PRIV_RISK** — user gained privileged role but has noncompliant or no device.

**Output:**
```
⚠️ Privilege Escalation Detected
Events (last 7 days): 2

| time | user | role added | actor | device compliance | flags |
|------|------|------------|-------|-------------------|-------|

Risk Assessment
- jsmith@northwind.com gained Global Admin — device compliant ✅
- newuser@northwind.com gained User Admin — no managed device ⚠️ PRIV_RISK
```

**Fields used:**
- Entra: `list_directory_audits` (operationType, targetResources, initiatedBy), `get_user`, `list_role_assignments`
- Intune: `search_managed_devices`

---

## U10 — "device offboarding audit"

**Intent:** Identify devices that should be wiped or retired.

**Procedure:**
1. intune `list_managed_devices` → find:
   - ORPHAN devices (owner `accountEnabled=false` or no match)
   - Devices with `lastSyncDateTime` >30 days
   - Devices with `managementState` ≠ managed
2. For each: entra `get_user` → confirm owner status.
3. intune `list_audit_events` → check for recent wipe/retire attempts.
4. Flag: **OFFBOARD_GAP** — orphaned device with old sync, should be wiped.

**Output:**
```
⚠️ Device Offboarding Gap
Devices requiring attention: 2

| device | owner | owner status | compliance | lastSync | flags |
|--------|-------|--------------|------------|----------|-------|

Recommendations
- WINDEV2407EVAL: owner disabled, last sync 45d ago — initiate wipe
- OLDDEVICE01: no owner match, last sync 60d ago — retire
```

**Fields used:**
- Intune: `list_managed_devices` (complianceState, lastSyncDateTime, managementState, userPrincipalName)
- Entra: `get_user` (accountEnabled)
- Intune: `list_audit_events`

---

## U15 — "data exfiltration investigation"

**Intent:** Correlate a suspicious identity signal with the compliance evidence that would
scope its blast radius.

**Procedure:**
1. entra `list_sign_ins` (riskLevelAggregated ≠ none) → establish the actor and window.
2. entra `list_directory_audits` → what the actor changed in that window.
3. purview `list_ediscovery_cases` (status=active) → is this actor already in scope of a
   case? Cross-check with purview `list_ediscovery_custodians` per active case.
4. purview `list_threat_assessment_requests` → any mail/URL/file assessments in the window.
5. Flag: **DATA_EXFIL** — risky sign-in or audit burst by a user who is a custodian on an
   active eDiscovery case, or the subject of a threat assessment.

**Output:**
```
🚨 Possible Data Exfiltration
Actor: <upn>  Window: <ISO>..<ISO>

| signal | source | detail | flags |
|--------|--------|--------|-------|

Compliance context
- Active cases naming this actor as custodian: N (holdStatus: ...)
- Threat assessments in window: N
```

**Fields used:**
- Entra: `list_sign_ins` (riskLevelAggregated, createdDateTime, userPrincipalName),
  `list_directory_audits` (activityDisplayName, initiatedBy, activityDateTime)
- Purview: `list_ediscovery_cases` (status), `list_ediscovery_custodians` (email, holdStatus),
  `list_threat_assessment_requests` (category, contentType, status, createdDateTime)

---

## U16 — "insider risk assessment"

**Intent:** Assess one person's compliance exposure — what they can reach, what is held,
what retention says about it.

**Procedure:**
1. entra `get_user` + `list_role_assignments` → privilege level.
2. purview `list_ediscovery_cases` → for each non-closed case,
   purview `list_ediscovery_custodians` → is this user a custodian, and is the hold applied?
3. purview `list_ediscovery_noncustodial_data_sources` → sources attached without a custodian.
4. purview `list_retention_labels` (delegated only) → labels that delete without a record
   declaration, i.e. where evidence can age out.
5. Flags: **INSIDER_RISK** (privileged user who is a custodian on an active case),
   **HOLD_GAP** (custodian on an active case whose hold is not applied, or released while
   the case is still active).

**Output:**
```
⚠️ Insider Risk Assessment — <upn>
Privilege: <roles or none>

| case | role on case | holdStatus | case status | flags |
|------|--------------|------------|-------------|-------|

Retention exposure
- Labels deleting without record declaration: N (evidence may age out)
```

**Fields used:**
- Entra: `get_user` (accountEnabled), `list_role_assignments`
- Purview: `list_ediscovery_cases`, `list_ediscovery_custodians` (holdStatus, releasedDateTime),
  `list_ediscovery_noncustodial_data_sources`, `list_retention_labels`
  (behaviorDuringRetentionPeriod, actionAfterRetentionPeriod, isInUse)

---

## Flag-Rule Precision

- **CONTRADICTION** — normalize both to boolean: Intune `complianceState === 'compliant'`; Entra `deviceDetail.isCompliant === true`. Flag only when both present and differ. Always print sign-in timestamp.
- **STALE** — `complianceState === 'compliant'` AND `now - lastSyncDateTime > 7 days`. Threshold is default; user can name another window.
- **ORPHAN** — device `managementState === 'managed'` AND owner `accountEnabled === false` OR no Entra match.
- **RISKY_SIGNIN** — `riskLevelAggregated` in (medium, high) on a managed device.
- **MFA_WEAK** — privileged user with `status.errorCode` in (500199, 65001) or `riskLevelAggregated` ≠ none.
- **PRIV_RISK** — user with privileged role AND noncompliant device or no device.
- **OFFBOARD_GAP** — ORPHAN device with `lastSyncDateTime` >30 days.
- **DATA_EXFIL** — user with `riskLevelAggregated` in (medium, high) OR an audit burst,
  AND that user's `userPrincipalName` matches a custodian `email` on a case whose `status`
  is not `closed`. Case-insensitive match; never join on display name.
- **INSIDER_RISK** — user holds a privileged role AND is a custodian on a non-closed case.
- **HOLD_GAP** — custodian on a non-closed case whose `holdStatus` is not `applied`, or
  whose `releasedDateTime` is set while the case `status` is `active`. This is a compliance
  finding in its own right — report it even when no identity signal fired.

## Degradation

- intune unavailable → answer identity-only from entra, prefix: `(device plane unavailable — intune MCP not reachable)`.
- entra unavailable → answer device-only from intune, prefix: `(identity plane unavailable — entra MCP not reachable)`; cannot compute CONTRADICTION, RISKY_SIGNIN, MFA_WEAK, PRIV_RISK — say which flags are uncomputable.
- 403 from either → likely missing Graph permission or (intune) no Intune license; report remediation, don't retry blindly.
- purview unavailable → answer identity/device-only, prefix `(compliance plane unavailable —
  purview MCP not reachable)`; DATA_EXFIL, INSIDER_RISK, and HOLD_GAP are uncomputable — say so.
- `purview.list_retention_labels` absent is NOT an outage: `RecordsManagement.Read.All` is
  delegated-only, so the tool does not exist when purview_mcp runs app-only. Say
  "retention posture unavailable (purview running app-only)" and continue — the eDiscovery
  flags are unaffected.

## Hard Rules

- Read-only. Never call write/confirm-gated tools.
- Never echo tokens, secrets, or raw credential fields; rely on MCPs' redaction.
- Join on UPN / userId / deviceId↔azureADDeviceId / custodian `email`↔UPN only — never display name.
- eDiscovery output is legally sensitive and may be privileged. Report case IDs and hold
  status; never quote `contentQuery` search terms or review-set content into a shared summary.

---

## U17 — "audit app registrations and blast radius"

**Intent:** Detect high-risk enterprise applications, critical blast radius scores, and expiring credentials.

**Procedure:**
1. Call entra `audit_app_registrations` (or CLI `bun run cli entra apps audit`).
2. For identified high-risk applications, call entra `get_app_blast_radius` (or `bun run cli entra apps blast-radius <appId>`).
3. Call entra `audit_credential_hygiene` (or `bun run cli entra apps hygiene --threshold-days 30`) to bucket expired/expiring secrets.
4. Emit findings table: App Display Name · App ID · Blast Radius Score · Risk Level · Expired Creds · Expiring Creds · Flags.
5. Apply flags: `APP_RISK`, `HYGIENE_RISK`.

---

## U18 — "audit standing PIM dormancy"

**Intent:** Uncover standing, unused privileged role eligibilities exceeding 90 days.

**Procedure:**
1. Call entra `audit_dormant_pim_eligibility` (or CLI `bun run cli entra roles dormant-pim --days 90`).
2. Cross-reference users with `list_sign_ins` to verify active usage vs dormancy.
3. Apply flag: `DORMANT_PRIV`.

---

## U19 — "audit unscoped mail and SharePoint permissions"

**Intent:** Find applications holding tenant-wide `Mail.*` permissions without application access policies, or overly broad `Sites.Selected` grants.

**Procedure:**
1. Call exchange `audit_unscoped_mail_access` (or CLI `bun run cli exchange apps audit-mail`).
2. Call purview `audit_sites_selected` (or CLI `bun run cli purview sites audit`).
3. Cross-reference service principal IDs against entra `get_service_principal`.
4. Apply flag: `UNSCOPED_ACCESS`.

---

## U20 — "validate domain SPF configuration"

**Intent:** Verify DNS SPF records for all accepted domains to prevent spoofing and ensure RFC 7208 lookup limits (≤10) are not breached.

**Procedure:**
1. Call exchange `validate_domain_spf` (or CLI `bun run cli exchange domain validate-spf`).
2. Verify: Record present, valid syntax, lookup count ≤ 10, softfail/hardfail policy.
3. Apply flag: `SPF_MISCONFIG`.

---

## U21 — "tenant security posture scorecard"

**Intent:** Comprehensive multi-plane posture scorecard evaluating all 5 Graph planes.

**Procedure:**
1. Run Unified CLI `bun run cli triage posture` (or `--markdown`).
2. Alternatively query concurrently through the gateway:
   - `entra.audit_credential_hygiene`
   - `defender.audit_threat_indicators`
   - `intune.audit_firewall_policies`
   - `exchange.audit_forwarding_rules`
   - `purview.audit_retention_cases`
3. Score tenant health (`HEALTHY`, `NEEDS_ATTENTION`, `CRITICAL_RISK`).
4. Generate prioritized remediation recommendations.

---

## U22 — "mailbox forwarding & BEC exfiltration sweep"

**Intent:** Detect inbox rules forwarding, redirecting, or deleting emails (key indicators of Business Email Compromise exfiltration).

**Procedure:**
1. Run `bun run cli triage user <upn>` or call exchange `audit_forwarding_rules`.
2. Inspect `suspiciousRules` array for external email destinations (`forwardTo`, `redirectTo`) and auto-delete actions (`delete: true`).
3. Apply flag: `BEC_FORWARDING`.

---

## U23 — "endpoint firewall posture & compliance audit"

**Intent:** Audit Windows Firewall policy health and eliminate legacy classic profile drift across managed endpoints.

**Procedure:**
1. Run `bun run cli triage device <deviceId>` or call intune `audit_firewall_policies`.
2. Inspect `endpointSecurityPoliciesCount` vs `classicProfilesCount`.
3. Verify that managed devices have active BitLocker/FileVault encryption and compliance policies assigned.
4. Apply flags: `FIREWALL_GAP`, `CLASSIC_PROFILE`.

---

## U24 — "threat intelligence indicators & incident correlation"

**Intent:** Correlate ingested threat intelligence indicators with active high-severity Defender alerts.

**Procedure:**
1. Call defender `audit_threat_indicators` (or CLI `bun run cli defender indicators audit`).
2. Inspect `activeHighAlertsCount` and matching indicator actions (`alertAndBlock`, `alert`).
3. Apply flag: `THREAT_ALERT`.

---

## U25 — "purview compliance retention & legal hold audit"

**Intent:** Verify that custodians and active legal disputes maintain unbroken hold coverage and compliant retention schedules.

**Procedure:**
1. Call purview `audit_retention_cases` (or CLI `bun run cli purview cases audit`).
2. Check for active cases without holds or unapplied custodian holds.
3. Apply flag: `RETENTION_GAP`.

---

## Audit Logging Procedure

After EVERY invocation, append an entry to `AUDIT.md`. This is the safety net.

### Log Entry Format

```markdown
## YYYY-MM-DDTHH:MM:SSZ — Session [session_id]

**Question:** "[user's question]"

**Scenario:** U[number] ([scenario name])

**Tools Called:**
1. `[tool_name]` → [param]: [value]
2. `[tool_name]` → [param]: [value]

**Findings:**
- [key finding 1]
- [key finding 2]

**Flags Fired:** [list or "None"]

**Actions:** [what was returned to user]

**Safety Check:**
- [ ] No secrets/tokens logged
- [ ] No write tools called
- [ ] Read-only operations only
- [ ] Graceful degradation (if applicable): [state which plane was missing]
```

### What to Log

| Field | Description |
|-------|-------------|
| Timestamp | ISO 8601 format |
| Question | Exact user question |
| Scenario | U1-U10 triggered |
| Tools Called | Tool name + redacted params (mask IDs: `a7543999-...`) |
| Findings | Summary only (no raw API responses) |
| Flags Fired | Which flags were raised |
| Actions | What was returned to user |
| Safety Check | Verify no unwanted actions |

### What NOT to Log

- Tokens, passwords, secrets
- Raw API responses (summarize only)
- Full device/user IDs (truncate: `a7543999-...`)
- Any PII beyond what's necessary for the audit

### Example Entry

```markdown
## 2026-06-30T15:49:00Z — Session ses_abc123

**Question:** "Is WINDEV2407EVAL really compliant?"

**Scenario:** U2 (Is device compliant?)

**Tools Called:**
1. `intune_get_managed_device` → device_id: "a7543999-..."
2. `entra_list_sign_ins` → user_principal_name: "jsmith@northwind.com"

**Findings:**
- Intune complianceState: compliant
- Entra deviceDetail.isCompliant: true
- Verdict: AGREE

**Flags Fired:** None

**Actions:** Returned compliance verdict to user.

**Safety Check:**
- [x] No secrets/tokens logged
- [x] No write tools called
- [x] Read-only operations only
- [x] Graceful degradation: N/A
```
