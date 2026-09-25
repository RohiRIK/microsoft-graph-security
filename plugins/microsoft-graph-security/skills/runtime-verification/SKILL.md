---
name: runtime-verification
description: "Runtime verification recipe for this MCP monorepo — how to drive gateway_mcp and its backends live over stdio JSON-RPC without mutating a real tenant. USE WHEN verifying a change to any *_mcp package or the gateway."
metadata:
  category: workflow
  effort: low
---

# verify

This repo has no test-runner surface worth trusting for verification (see
`/simplify` and `/code-review` guidance — build/tests prove CI, not the
running app). The real surface is `gateway_mcp` speaking MCP over stdio, since
that's how every real client (Claude Code, kilo.jsonc, etc.) talks to it.

## Launch

Spawn exactly like `.mcp.json` does:

```bash
bun run gateway_mcp/src/index.ts
```

Config comes from `settings.yaml` (resolved by `useProfile` before
`loadConfig`), not from `.env` files — those were retired to `.env.bak`. Point a
run at a different tenant with `MCP_SETTINGS=/path/to/settings.yaml`, or
`--profile <name>`. Backend entry points are absolute, so any cwd works.

`gateway_mcp/tests/server.smoke.test.ts` already does all of this and is the
faster way to check a change end to end.

Transport is **newline-delimited JSON-RPC 2.0 over stdin/stdout** (confirmed
from `node_modules/@modelcontextprotocol/server/dist/stdio.mjs` — no
Content-Length framing, unlike LSP). Backend connect/tool-count status prints
to **stderr**, not stdout — `[mcp-gateway] N/6 backends connected` before
tool calls will work.

## Drive

Write a small Node/Bun script that spawns the process above, sends one JSON
object per line to stdin (`{"jsonrpc":"2.0","id":N,"method":...}\n`), and
parses stdout line-by-line as JSON-RPC responses. Sequence:
`initialize` → `notifications/initialized` (no id, no response) → `tools/list`
→ `tools/call`. Tool names are namespaced `<backendId>.<toolName>` (e.g.
`entra.create_conditional_access_policy`, `intune.list_managed_devices`) —
see `gateway_mcp/src/backends/namespace.ts`.

## Verify without touching the real tenant

**Registering tool call auth is lazy** — `tools/list` and a `tools/call`
without `confirm: true` on a write tool never reach Microsoft Graph, so both
are safe to run against the real `.env` tenant with no side effects:

- `resources/list` proves the gateway is serving its backends' catalogs —
  16 URIs, including `gateway://session`, which names the tenant, the profile
  and its source. Reading it is the cheapest possible confirmation that a
  config change landed.
- `tools/list` proves schema plumbing (e.g. confirms
  `gateway_mcp/src/index.ts`'s `fromJsonSchema(tool.inputSchema)` is actually
  forwarding real params, not the old empty-object placeholder).
- `tools/call` on a `write_critical`/`write_destructive` tool **without**
  `confirm: true` hits `withGuardrail`'s HITL gate and returns a
  `confirmation_required` preview before any Graph request — confirms the
  guardrail without mutating anything live.
- A malformed-args `tools/call` (missing a required field) fails at MCP-SDK
  schema validation (`Input validation error: ... required property ...`)
  before even reaching the tool handler.

**Never send `confirm: true` on a write tool during verification** — that
executes for real against whatever tenant is configured in `settings.yaml`.

## Gotcha: write tools may not be registered at all

Each backend gates its whole `registerXWriteTools()` call behind
`<PREFIX>_ENABLE_WRITES`. If you're verifying a *new* write tool and it's
missing from `tools/list`, check `bun run status` first —
it's probably just off (this repo defaults every package to read-only via `settings.yaml`). To verify a write tool's schema/HITL
behavior, either drive the **backend directly** (`bun run <pkg>/src/index.ts` with
`<PREFIX>_ENABLE_WRITES=true` in that one command's environment — standalone, an explicit
variable still outranks `settings.yaml`), or boot the gateway with
`MCP_SETTINGS=<scratch settings.yaml>` that sets `enableWrites: true` for that plane.
**Setting `<PREFIX>_ENABLE_WRITES` on the gateway's environment does nothing** (since
2026-09-23): the gateway strips every plane write flag before spawning a backend
(`backendEnv` in `gateway_mcp/src/backends/proxy.ts`), so a stray shell variable can never
outrank `settings.yaml`.

## Gotcha: interactive delegated sign-in can hang verification

If a backend has `accessMode: delegated` with a real (non-`wellknown`
or already-cached) flow, calling a **read** tool can trigger a live
interactive browser sign-in and block. Stick to `tools/list` and
unconfirmed `tools/call` on write tools to stay auth-free.

## settings.yaml

`bun run doctor` is the fastest check that config resolves and credentials are
present; `--sign-in` additionally contacts Graph. `bun run migrate --check`
reports drift against any remaining `.env`. Both are read-only.

A bad `activeProfile`, a tenant outside its own allowlist, or a
`clientId: wellknown` under `app_only` all fail loud at startup with a clear
message rather than silently degrading.

## Gotchas

- **The audit log uses WAL, so the `.db` mtime never moves.** Writes land in `<db>-wal`.
  Checking freshness by stat'ing the `.db` file shows nothing happening while rows are being
  written — cost a whole dogfood session once. Read it with `bun run audit list` instead.
- **A tool call through your MCP client and one you drive from Bash are different processes.**
  The client's gateway resolved its settings when it started, possibly days ago and possibly
  against another tenant. Read `gateway://session` before trusting what a live call proves.
- **Never send `confirm: true`.** An unconfirmed write returns a preview and touches nothing —
  that IS the test. Sending it executes against a real tenant.
- **Schema validation happens before the guardrail.** A call rejected for a bad argument never
  reaches the handler and is never audited, which is correct but looks like a missing row.
