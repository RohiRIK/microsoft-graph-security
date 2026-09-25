# auth-ops — Scope Rules

Facts about Microsoft Graph permissions that this repo has paid for by getting wrong.

## Verify a scope before you add it

Graph publishes some permissions as **application-only**. Requesting one in a delegated
sign-in does not merely fail to grant it — Entra rejects the **entire** request:

```
AADSTS650053: The application 'Microsoft Graph Command Line Tools' asked for scope
'ThreatAssessment.Read.All' that doesn't exist on the resource
```

25 valid scopes were lost to one invalid one. Check first, at
<https://learn.microsoft.com/en-us/graph/permissions-reference>: find the permission and read
its table. A `-` in the **Delegated** column means there is no delegated form.

| Scope | Delegated? | Consequence here |
|---|---|---|
| `ThreatAssessment.Read.All` | **No** — app-only | purview's threat-assessment tools are app-only |
| `RecordsManagement.Read.All` | Yes — delegated only in practice | purview registers retention tools only under delegated |
| `Machine.Read.All` | App-only | Defender endpoint plane requires `accessMode: app_only` |
| `Policy.Read.All` | Yes | Looks app-only if you grep sloppily — it is not |

## Where scopes live

- `<pkg>/src/config.ts` → `DELEGATED_READ_SCOPES` — what a delegated sign-in requests.
- `<pkg>/src/config.ts` → `APP_ONLY_READ_SCOPES` — no delegated form exists.
- `<pkg>/src/catalog.ts` → `PERMISSION_CATALOG` — permission → the tools it gates.

Every scope in `DELEGATED_READ_SCOPES` must be justified by a registered tool. Each package's
`tests/least-privilege.test.ts` enforces it, and it fails the build — that test is the reason
two unused Mail scopes were found and removed.

## Adding a scope

1. Confirm it has a delegated form (table above / permissions reference).
2. Add it to `DELEGATED_READ_SCOPES` **and** `PERMISSION_CATALOG`, mapped to the tools that
   need it. The least-privilege test fails if you do only one.
3. `bun run doctor --sign-in` — it will report the scope as not granted until consent.
4. Print the consent step for the operator. **Do not grant it.**

## Not every permission is a scope

Some access comes from an **admin role**, not from Entra consent. DLP configuration (Security &
Compliance PowerShell) needs a Purview role — *View-Only DLP Compliance Management* is enough to
read it — assigned in the Purview portal. For such tools:

- `requiredPermissions: []` in `risk.ts`, and **nothing** in `PERMISSION_CATALOG` or
  `DELEGATED_READ_SCOPES` — those are requested at sign-in, and a Purview role is not a Graph
  scope (it would fail the sign-in like `ThreatAssessment.Read.All` did).
- Name the role in the tool's description, so a refusal is diagnosable.
- Granting the role is the operator's, like consent.

## Removing a scope

Removing is always safe to propose: an ungranted scope is a 403 on one tool, while an
over-granted one is standing access to a client's data. If no registered tool needs it, it goes.
