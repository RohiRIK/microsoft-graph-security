# Run Workflow

Start the MCP Gateway and all registered backends.

## Prerequisites

- Setup completed (`settings.yaml` exists at repo root)
- Target tenant profile configured and active

## Start

```bash
cd gateway_mcp
bun run dev
```

Or via the CLI directly:
```bash
bun run src/cli.ts dev
```

## What you see on startup

```
[mcp-gateway] Config loaded: tenant=xxx, mode=app_only, writes=false
[mcp-gateway] Auth provider ready (app_only).
[mcp-gateway] Connecting to backends...
[mcp-gateway] Connected to backend entra (N tools).
[mcp-gateway] Connected to backend intune (N tools).
[mcp-gateway] Connected to backend exchange (N tools).
[mcp-gateway] 3/3 backends connected.
[mcp-gateway] 3 backends registered: entra, intune, exchange.
[mcp-gateway] N namespaced tools aggregated (M raw-name collisions resolved by prefixing).
[mcp-gateway] Read-only posture inherited; writes off by default.
```

If a backend fails to connect, you'll see `Failed to connect backend X` on stderr. The gateway still starts with the remaining backends.

## Check status

```bash
bun run status              # human-readable
bun run status --json       # JSON output
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Config loaded" but no "Connecting to backends" | Missing required tenant configuration | Check `settings.yaml` has `tenant.id` and accessMode configured |
| "Failed to connect backend X" | Backend misconfigured | Check plane configuration and tenant allowlist in `settings.yaml` |
| Sign-in browser never returns | Loopback listener blocked | MSAL picks an ephemeral localhost port; check a firewall is not blocking localhost. There is no port setting — Azure AD matches `http://localhost` on any port for a public client |
| "Module not found" | Dependencies not installed | Run `bun install` in `gateway_mcp/` |

## Gotchas

- The gateway process stays running on stdio. It's designed to be spawned by an MCP client (like Claude Code via `.mcp.json`), not run as a standalone daemon.
- SIGINT/SIGTERM triggers graceful shutdown — kills all backend child processes.
- Backend tools are discovered at startup. If a backend adds tools at runtime, the gateway won't see them until restart.
