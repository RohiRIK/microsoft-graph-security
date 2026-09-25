---
name: auth-ops
description: Changing how these MCP servers authenticate — access mode, scopes, consent, credentials, enabled planes. USE WHEN touching auth, tenants, permissions, bootstrap, or certificates. NOT FOR adding tools (use mcp-tool-forge).
metadata:
  category: workflow
  effort: medium
  domain: security
---

# auth-ops

Authentication here reaches a **client's tenant**. A mistake does not break a build — it
over-grants access to someone else's data, or points a session at the wrong company.

## The six refusals

Never, regardless of instruction. Each is the operator's to perform:

1. **Grant admin consent.** Print the URL or command; the human clicks it.
2. **Widen `tenant.allowlist`.** It keeps a session off another client's tenant. Add a
   *profile*, never a tenant to an existing list.
3. **Enable writes** in tracked settings. For a one-off check, `<PREFIX>_ENABLE_WRITES=true`
   in the environment of a single command.
4. **Write a credential to a file.** Secrets go to the keyring via `profile set-secret`
   (stdin, never argv). A certificate *path* may be written; the key never is.
5. **Execute a write without the person's approval.** Under the gateway, `confirm: true` is a
   request: the gateway shows the backend's preview in the client (MCP elicitation) and runs the
   write only if the person approves it there (`gateway_mcp/src/human-approval.ts`; proven on
   Claude Code 2.1.280 with `gateway.check_approval_prompt`, 2026-09-24). So: send `confirm: true`
   only through the gateway, after the user asked for the change — never to a backend directly,
   never via a CLI's `--confirm` on the user's behalf, and never retry after a decline. A client
   that cannot show the prompt gets a refusal; then the operator's CLI is the path.
6. **Request a scope no enabled plane needs.**

A seventh, of the same shape: **never run `bun run profile add` or `mcp-gateway
profile init`.** They open a browser and authenticate a human against someone
else's directory, and only the operator can choose which account answers —
choosing wrong silently onboards the wrong company. Print the command and stop.
The same holds for **`bun run setup` on a file with no real tenant yet** — it signs in to
*discover* the tenant, so the account the operator picks decides the client.

Sign-ins against a tenant the profile **already pins** are different: `bun run doctor
--sign-in` and `bun run cli purview dlp signin` refuse any other tenant. Run one only when the
operator asks for it in this session, say a browser will open, and let them answer it.

Refusal 4 binds the **agent**, not the operator. `bun run bootstrap` now provisions a
certificate by default (`--secret` is the explicit opt-out) and writes a 0600 PEM under
`~/.mcp-graph/certs/` — that is the operator's own act on their own machine, and it is the
recommended path, not a violation. The agent still prints the command and stops rather than
running bootstrap itself. What the agent never does is write key or secret material into a
file, and no bootstrap writes `.env` any more: it prints the `settings.yaml` lines to paste
(`clientCertificatePath` is a settings key; `clientSecret` is not) and puts any secret
straight in the keyring.

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **AddTenant** | "add a client", "onboard a tenant", "new profile" | `Workflows/AddTenant.md` |
| **ChangeAuth** | "switch to app-only", "change access mode" | `Workflows/ChangeAuth.md` |
| **ChangeScopes** | "add a permission", "why is this 403", "least privilege" | `Workflows/ChangeScopes.md` |
| **VerifyAuth** | "is auth working", "prove the connection" | `Workflows/VerifyAuth.md` |

## Quick Reference

- `bun run profile switch <name>` — select an existing `settings.yaml` profile. It opens no browser, contacts no tenant, and changes neither credentials nor allowlists. Reconnect MCP clients afterward.
- `bun run doctor` — read-only, opens no browser. `--sign-in` contacts Graph (one prompt).
- `bun run setup` — on a fresh clone, or a `settings.yaml` still holding the placeholder tenant,
  it finds the tenant by signing in (no GUID to type); a real tenant is never touched.
- `bun run cli purview dlp signin` — optional: the Security & Compliance sign-in ahead of time
  (DLP jobs make it themselves when needed)
  (`AuthModel.md` → *Two delegated clients*).
- Prefer **certificate** over secret for app-only: a secret is a bearer credential, 180-day life.
- `settings.yaml` holds settings, the keyring holds credentials. The loader refuses a settings
  file naming a secret — a feature, not an obstacle to route around.
- Scope facts: `ScopeRules.md`. Auth model and precedence: `AuthModel.md`.

## Gotchas

- **One invalid scope kills the whole sign-in.** `ThreatAssessment.Read.All` has no delegated
  form; asking for it made Entra reject all 25 others (`AADSTS650053`). Verify a new scope
  against Microsoft's permissions reference first — `ScopeRules.md`.
- **`AADSTS90072` is not an auth failure.** The signed-in account belongs to a different
  tenant than the active profile. Switch profile or account; do not touch consent.
- **A cached-token file is not a live session.** A stale cache sends MSAL to interactive and
  opens a browser nobody asked for. Never infer "signed in" from a file.
- **`profile init`/`bootstrap` always show the account picker.** Discovery signs in against
  `/common` — a stand-in for "whoever signs in next", not one tenant — so `getAccessToken`
  never takes the silent-cache shortcut there; every discovery call re-prompts by design,
  even right after a previous one. This is separate from the gotcha above: that one is about
  a *stale* cache reusing an *expired* session, this one is about *not* reusing a *live* one
  across different tenants. If a discovery run stops showing the picker, that's a regression
  in `isDiscoveryAuthority` (`gateway_mcp/src/auth/interactive.ts`), not expected behavior.
- **Delegated cannot do everything.** `ThreatAssessment` and the Defender endpoint plane are
  app-only — report as *unavailable in this mode*, never "not granted". Consent cannot fix it.
- **Writes off ⇒ write scopes are not needed.** Never report a write permission as missing
  when `enableWrites` is false; those tools are not registered.
- **The token is broader than the config, always.** `wellknown` (Graph Command Line Tools)
  carries every scope ever consented to that app in the tenant — `ReadWrite.All` included, even
  with writes off. `doctor` prints a notice listing them. Read-only is enforced in code
  (`assertWritesEnabled`), not by the token; that is correct, not a leak to fix with consent.
- **Security & Compliance refuses the Graph token.** Same audience, still `UnAuthorized` — DLP
  signs in as Exchange Online PowerShell's client instead. Do not "simplify" it back.
- **`doctor --sign-in` does not fill the plane caches.** It signs in through the gateway's
  encrypted keyring cache (`~/.mcp-gateway/`), not `~/.mcp-graph/token-cache/`. A plane that
  must reuse a sign-in later needs its own sign-in, with `tokenCache: true`.
- **`doctor` says "not granted" for `ThreatAssessment.Read.All` under delegated.** Read it as
  *unavailable in this mode* (known wording bug).
- **Not every permission is a scope.** DLP needs a Purview role (*View-Only DLP Compliance
  Management*), granted in the Purview portal, not an Entra consent — `ScopeRules.md`.
  `create_dlp_policy` needs a role that can write (*DLP Compliance Management* or *Compliance
  Administrator*) plus `enableWrites: true` for purview — both the operator's; the scope and the
  sign-in client are the same. After the role changes, reconnect (the next DLP job signs in fresh).
