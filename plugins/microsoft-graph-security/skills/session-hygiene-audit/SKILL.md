---
name: session-hygiene-audit
description: Audit which delegated sign-in sessions are active across entra/intune/defender/purview, their age against tokenCacheMaxAgeHours, and disconnect stale ones. USE WHEN multiple agents/operators may be sharing a dev tenant, a delegated session seems to have persisted longer than expected, or setting up token-cache TTL policy for a new environment. NOT FOR revoking a compromised user's sign-in sessions in the tenant itself (use entra.revoke_sign_in_sessions via security-ops's HostileOffboarding/incident workflows — this skill covers the MCP servers' own delegated auth sessions, not tenant user sessions).
metadata:
  category: workflow
  effort: low
  tags: entra, intune, defender, purview, token-cache, session-hygiene
---

# session-hygiene-audit

Born from a real incident this session: two independent AI agents (this one and Kilo Code)
signed in against the same live dev tenant, and a delegated session was found still alive
a full day after the initial sign-in — with no TTL, `ENTRA_TOKEN_CACHE=true` meant a
persisted session survived indefinitely. All four delegated-auth packages now enforce a
dual TTL (file mtime + in-memory `accountCachedAt`, default 24h, `*_TOKEN_CACHE_MAX_AGE_HOURS`
to override) — this skill is how you check that it's actually configured and working, not
just present in code.

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **AuditActiveSessions** | "who's still connected", "check session age", "is this connection stale" | `Workflows/AuditActiveSessions.md` |

## Ground Rules

1. **Two independent expiry checks exist per package**: the token-cache *file*'s mtime (bounds reuse across separate CLI invocations) and an *in-memory* `accountCachedAt` timestamp (bounds reuse within one long-running MCP server process, since the file's mtime gets refreshed on every write and won't naturally age out for a process that keeps calling `getAccessToken`). Check both when auditing, not just one.
2. **A shared dev tenant with multiple agents/operators needs a shorter TTL than a single-operator prod environment** — the default 24h is a starting point, not a mandate; recommend tightening it (e.g. 4-8h) for shared test tenants.
3. `disconnect_session` (where it exists — `entra_id_mcp`, `intune_mcp`) forcibly clears the in-memory account, removes it from the MSAL cache, and deletes the cache file — use it instead of waiting out the TTL when you know a session should end now (e.g. handing the tenant off to another agent/operator).

## Gotchas

- Restarting the MCP server process resets the in-memory `accountCachedAt` clock even if the underlying file cache is still within its own TTL window — a restarted process can grant up to another full `tokenCacheMaxAgeHours` from the restart, not from the true original sign-in time. Low severity (exploiting it requires either control over restarts or filesystem access to the cache file, which already exposes the tokens directly) but worth knowing when reasoning about "how long could this really have been alive."
- `defender_mcp` and `purview_mcp` have the TTL config and file-cache expiry but **no `disconnect_session` tool** — the only way to force-end a session in those two packages is to delete the cache file directly or wait out the TTL.
- Checking `ENTRA_TOKEN_CACHE_MAX_AGE_HOURS` (or the per-package equivalent) in `.env` shows the *configured* value — it does not tell you the *actual* age of a currently-cached session; that requires checking the cache file's `mtime` directly.

## Examples

**Example 1: Shared dev tenant handoff**
```
User: "I'm handing this dev tenant off to another agent for testing — make sure my session doesn't linger"
→ AuditActiveSessions → checks cache file mtime + confirms disconnect_session exists for the package in use
→ Calls entra.disconnect_session / intune.disconnect_session → confirms cache file removed
```

**Example 2: "Why am I still signed in from yesterday?"**
```
User: "It's been over a day and I still seem connected — is that a problem?"
→ AuditActiveSessions → checks ENTRA_TOKEN_CACHE_MAX_AGE_HOURS (default 24) against actual cache file age
→ If within 24h: expected, explains the TTL. If beyond: flags as a bug — should have been auto-expired
```
