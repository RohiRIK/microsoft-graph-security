# auth-ops — The Auth Model

## Three paths, different capabilities

| Path | Setup cost | Cannot do |
|---|---|---|
| Delegated + `clientId: wellknown` | None — no app registration, no consent | `ThreatAssessment`, Defender endpoint plane, anything the signed-in user cannot do |
| Delegated + own app | Registration + admin consent | Same ceiling; buys attribution to your app |
| App-only + certificate | Registration, certificate, consent | Nothing — but no user context, and no browser |

Delegated is the default. It acts **as the signed-in human**, inheriting their Conditional
Access and MFA, which is why it is the right default for an investigator.

App-only is required for unattended runs (`scripts/revoke-timer/`) — nobody is there to
complete a browser sign-in.

## Two delegated clients

| Client | Used for | Token cache | Who signs in |
|---|---|---|---|
| Microsoft Graph Command Line Tools (`14d82eec…`, `clientId: wellknown`) | Every Graph plane | `~/.mcp-graph/token-cache/<tenant>-14d82eec….json` — shared by all planes (one prompt) | The plane on first use; `doctor --sign-in` uses the gateway's own cache instead |
| Exchange Online PowerShell (`fb78d390…`) | Security & Compliance PowerShell — DLP export, plan, dry run, create | `~/.mcp-graph/token-cache/<tenant>-fb78d390….json` | The DLP job itself (browser, inside the job) when there is no current sign-in; or ahead of time, `bun run cli purview dlp signin` |

Both are delegated (the operator's MFA and Conditional Access), bound to the profile's tenant,
cached only with `tokenCache: true`, and reused silently only within `tokenCacheMaxAgeHours` of
the last interactive sign-in. The second one is made by the DLP job that needs it — the same as a
Graph plane on its first tool call — and ends when the gateway's session ends (the gateway
removes its cache and marker), so a reconnect signs in to both again. Why two: the Security & Compliance service accepts
tokens from its own module's client and refuses a Graph Command Line Tools token for the same
audience (tested 2026-09-23). Neither token enforces read-only; the code does.

## Settings precedence, top wins

```
shell env  >  <pkg>/.env  >  packages.<pkg>  >  defaults  >  built-in default
```

`settings.yaml` is where you **manage**; an environment variable is a one-off **override**.
This is why a verification-only change (`EXCHANGE_ENABLE_WRITES=true bun run doctor`) never
has to touch the tracked source of truth.

**Except under the gateway, for write flags.** A backend the gateway spawns never inherits a
`<PREFIX>_ENABLE_WRITES` variable (`backendEnv`, `gateway_mcp/src/backends/proxy.ts`), so for
a gateway session `settings.yaml` is the only place writes turn on. Standalone commands keep
the precedence above.

## Switching clients

One profile owns one tenant and its own fail-closed allowlist. Switch clients with
`bun run profile switch <name>`, then reconnect the MCP client. This changes only
`activeProfile`; it does not sign in, contact Graph, grant consent, modify credentials,
enable writes, or widen an allowlist. The selected account still must be a member or guest
of the target tenant when interactive sign-in is needed.

For a one-off command without changing the active profile, run
`bun run with-profile <name> -- <command>`. It validates the canonical profile and passes
`MCP_PROFILE` only to that child process. For example,
`bun run with-profile northwind -- bun run doctor --sign-in` leaves `settings.yaml` unchanged.

## Where credentials live

- **OS keyring** (macOS Keychain / Windows DPAPI / Linux libsecret), one entry per profile per
  package: `printf %s "$SECRET" | mcp-gateway profile set-secret <profile> --package <pkg>`
- **Certificate**: a PEM path in settings; the key file itself never enters the repo.
- **Never** in `settings.yaml` — the loader rejects a file naming a secret key.
- **Delegated token caches** — `~/.mcp-graph/token-cache/`, 0600, one file per tenant and client
  (see *Two delegated clients*); the gateway's own cache is encrypted under `~/.mcp-gateway/`.
  `bun run prune-caches` lists them; `revoke` ends the gateway session server-side.

## Enabled planes

`enabled: false` on a package means the gateway does not spawn it **and** bootstrap does not
request its scopes. An identity-only engagement asks a client's admin for 12 permissions
instead of 28. Absent means enabled, so existing profiles are unaffected.
Because an absent plane still reaches the tenant, `doctor`, the gateway's boot log and
`gateway://session` mark it: "enabled by default — not listed in settings.yaml" (issue #11;
making the list explicit-only is the planned second step).

## Fail-closed controls, and why they stay

- **Tenant allowlist** — a tenant not on the list refuses to start. It is what keeps a
  colleague's session off another client's tenant. Never widened to make something work.
- **Writes off by default** — write tools are not registered at all unless enabled.
- **HITL** — `write_destructive` / `write_critical` need `confirm: true` at call time, and
  optionally an out-of-band approval (threat model T-08).
- **Guardrail coverage** — a tool with no risk classification crashes the package at startup.
  Loud by design.
- **Session cap** — `GATEWAY_MAX_SESSION_AGE` (default 8h, `sessionMaxAge` in `defaults:`,
  or in a `gateway:` block to cap one profile shorter than the rest of the file). A
  gateway token cache older than the cap is deleted before MSAL reads it, and the tool call
  refuses rather than opening a browser nobody asked for. Age is measured from last use, so a
  session in continuous work is not interrupted. It was documented and unenforced until
  2026-08-10 — see `docs/specs/tenant-safety.md`.
- **No orphaned credentials** — delete a profile and its encrypted refresh tokens stay on
  disk. `bun run prune-caches` lists every cache and which profile owns it; `--delete`
  removes the ones no profile claims.
