# WrapExternalMcp

The capability belongs to an MCP whose source we do not control. Add it beside that server, not
inside it.

## Step 1: Pick the Form

| Need | Form | Cost |
|------|------|------|
| One-off, this session only | Keep the scratchpad script. No MCP at all. | none |
| Recurring, single tool, no auth complexity | Sidecar: one-file MCP server (Shape B, `Adapters.md`) run from the scratchpad or a `tools/` dir | low |
| Durable, multiple tools, or any write | New package in this repo following Shape A, registered as a gateway backend | high |

Do not build a package for a single read that runs once a month. Do not build a sidecar for
anything that mutates state — a mutation with no risk classification and no HITL gate has no
business existing.

## Step 2 (sidecar): Minimal Server

```ts
import { McpServer } from '@modelcontextprotocol/server';
import { StdioServerTransport } from '@modelcontextprotocol/server/stdio';
import * as z from 'zod/v4';

const server = new McpServer({ name: '<name>-sidecar', version: '0.1.0' });

server.registerTool(
  '<tool_name>',
  { description: '<what it does>', inputSchema: z.object({ /* ... */ }) },
  async (args) => ({ content: [{ type: 'text' as const, text: JSON.stringify(await run(args)) }] }),
);

await server.connect(new StdioServerTransport());
```

Wire it in `.mcp.json` as its own server entry, or as a gateway backend (Step 3). Credentials come
from env files — never inline.

## Step 3 (durable): Register as a Gateway Backend

1. Build the package per `Adapters.md` Shape A — including `risk.ts` and `catalog.ts`. A backend
   without risk classification does not get to join.
2. Export its `PERMISSION_CATALOG` and add it to `gateway_mcp/src/backends/catalogs.ts`. If the
   backend needs no tenant permission, follow the `LEARN_CATALOG` precedent: a key that names the
   fact rather than a fake permission.
3. Add a `BackendDescriptor` in `gateway_mcp/src/backends/registry.ts` — `stdio` with
   `command`/`args`/`envFile`, or `http` with `url`. Set `tokenInjection` deliberately.
4. Check namespacing: raw tool names colliding with an existing backend get prefixed differently
   (`findCollisions`, `backends/namespace.ts`). Confirm the exposed name before telling the user
   what to call.
5. `bun test gateway_mcp`, then restart the gateway — backends connect at startup.

## Step 4: Verify and Reconnect

Boot the gateway and read its stderr banner: backend count, aggregated tool count, collisions
resolved. Then have the user reconnect the MCP client and call the namespaced tool.

## Execution Log

```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"mcp-tool-forge","workflow":"WrapExternalMcp","status":"ok","duration_s":'$SECONDS'}' \
  >> ~/.claude/state/execution.jsonl
```
