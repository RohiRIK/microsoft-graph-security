---
name: gateway-bootstrap
description: Set up and run the MCP Gateway auth broker. USE WHEN bootstrapping the gateway, running gateway scripts, or troubleshooting gateway startup.
metadata:
  category: workflow
  effort: medium
---

# gateway-bootstrap

One-time setup and runtime commands for the MCP Gateway — the central auth broker fronting Entra ID, Intune, and Exchange Online MCP servers.

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **Bootstrap** | "bootstrap gateway", "setup gateway", "first time gateway" | `Workflows/Bootstrap.md` |
| **Run** | "run gateway", "start gateway", "dev gateway" | `Workflows/Run.md` |

## Quick Reference

| Command | What it does | When |
|---------|-------------|------|
| `bun run bootstrap` | Creates app registration, grants consent, provisions credentials | First time only |
| `bun run dev` | Starts gateway + all backends over stdio | Every run |
| `bun run status` | Check gateway configuration | Anytime |
| `bun run typecheck` | Type checking | Before commit |
| `bun run lint` | Biome lint + format | Before commit |
| `bun test` | Run all tests | Before commit |

All commands run from inside `gateway_mcp/`.

## CLI Commands

```bash
mcp-gateway bootstrap           # one-time setup
mcp-gateway bootstrap --writes  # include write scopes
mcp-gateway dev                 # start gateway
mcp-gateway status              # check config (human-readable)
mcp-gateway status --json       # check config (JSON, pipes to jq)
mcp-gateway --help              # show help
mcp-gateway --version           # show version
```

## Gotchas

- Bootstrap requires interactive browser sign-in — it opens a browser window for loopback redirect on `localhost:7842`. Port must be free.
- Bootstrap is idempotent — running it twice reuses the existing app registration (tag-based lookup with `ConsistencyLevel: eventual` header). Missing the header = 400 error, not "app not found".
- `settings.yaml` stores non-secret profile configuration; secrets live in the OS keyring and certificates in `~/.mcp-graph/certs/`. Never commit credentials.
- Backends (entra, intune, exchange, defender, purview) derive configuration from `settings.yaml` (or the active profile). The gateway spawns enabled backends as child processes.
- `bun run dev` spawns enabled backends as child processes. If one fails to connect, the gateway still starts with the remaining tools. Check stderr for "Failed to connect backend" messages.
- The gateway uses `bun`, not npm. Run `bun install` first if `node_modules/` is missing.

## Examples

**Example 1: First-time setup**
```
User: "set up the gateway"
→ Bootstrap workflow → bun run bootstrap → browser opens → .env written → ready to run
```

**Example 2: Start the gateway**
```
User: "run the gateway"
→ Run workflow → bun run dev → backends connect → tools discoverable
```

**Example 3: Check config as JSON**
```
User: "is the gateway configured?"
→ bun run status --json → pipes to jq
```
