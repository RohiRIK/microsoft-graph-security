---
name: mcp-tool-forge
description: Turns an ad-hoc script into a permanent, guardrailed MCP tool, or wraps an MCP whose source we cannot edit. USE WHEN a needed tool is missing, or when adding or changing a tool on any MCP server. NOT FOR authoring skills (use CreateSkill).
metadata:
  category: meta
  effort: medium
  domain: agents
---

# mcp-tool-forge

Close the loop between "no tool does this" and "a tool does this now": answer with a throwaway
script first, then offer once to promote it into a registered, risk-classified tool. Never edit
MCP source without a yes. The registration contract is derived per server (`ShapeContract.md`),
not assumed — so this works for any MCP, including ones we cannot edit.

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **DraftAdHocTool** | needed tool missing, "no tool for that", ad-hoc Graph call | `Workflows/DraftAdHocTool.md` |
| **PromoteToTool** | "yes, add it", "make that a real tool", "edit the MCP" | `Workflows/PromoteToTool.md` |
| **WrapExternalMcp** | target MCP source not editable (Notion, Learn, Gmail), "add a backend" | `Workflows/WrapExternalMcp.md` |
| **RollbackToolChange** | server fails to boot after a promotion, "undo the tool" | `Workflows/RollbackToolChange.md` |

## Quick Reference

- `ShapeContract.md` — 7 questions defining any server's contract. Read before touching one.
- `Adapters.md` — derived shape of this repo's packages and the gateway. Risk entry lands **first**.
- One offer per gap. Silence is not consent. Write tools need a second, separate confirmation.

## Gotchas

- A registered tool with no `risk.ts` entry **crashes the server at startup** — `verifyGuardrailCoverage()` throws and takes down every other tool with it.
- That coverage check reads a **hardcoded name list inside `register.ts`** (`ALWAYS_REGISTERED`, or the `Set` in entra). Adding the tool without adding the name there passes silently and skips the check.
- A new tool is invisible until the MCP client reconnects — tool lists are fetched at connect time, not polled.
- `import * as z from 'zod/v4'`, never `zod`. Write tools go in `writeRegister.ts`, never `register.ts`.
- A permission with no app-only equivalent gates **registration** (fail closed), not the call — see the purview retention-label precedent.
- Gateway namespacing: a raw name colliding with another backend changes the exposed tool name.
- `noConsole` is a Biome error in `src/`; scratchpad scripts stay in the scratchpad (untracked `dogfood-*.ts` at a package root is the anti-pattern).
- **A role is not a scope.** Access granted by an admin role (DLP: *View-Only DLP Compliance Management*) gets `requiredPermissions: []` and no `PERMISSION_CATALOG` entry — the catalog is requested at sign-in, and one invalid scope fails the whole sign-in.
- **30 s per call, ~60 KB per result.** The gateway abandons slower calls; clients reject larger results. Slow work becomes a `start_*` / `*_status` background job; large output is capped with an "N more" note. Measure on real data (`Adapters.md` → *Two limits*).
- **Editing `mcp_shared/` needs `bun install` in every package** — it is a `file:` dependency, copied, not linked.
- **`bun run verify:local` is the gate** (CI does not run). `--full` before a PR, results as a PR comment.

## Examples

```
User: "Which named locations does Conditional Access trust?"
→ no tool exists → DraftAdHocTool: script hits /identity/conditionalAccess/namedLocations, answers
→ "Promote to entra.list_named_locations?" → yes → PromoteToTool → bun test → reconnect

User: "Add a Notion tool that lists overdue tasks"
→ source not editable → WrapExternalMcp → sidecar server, or new gateway backend descriptor
```
