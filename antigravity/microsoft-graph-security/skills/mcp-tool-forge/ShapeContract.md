# mcp-tool-forge — Shape Contract

A "shape" is the set of edits a given MCP server requires to gain one tool. It is derived by
reading the server, never recalled from memory — packages drift, and a stale shape produces a
half-registered tool that takes the whole server down at startup.

`Adapters.md` holds shapes already derived for the servers in this repo. Treat it as a starting
hypothesis and re-verify the two load-bearing lines (guardrail wrapper, coverage check) with one
`grep` before editing.

## The 7 Questions

Answer all seven before proposing any edit.

| # | Question | How to answer |
|---|----------|---------------|
| 1 | Is the source editable, or third-party? | Is the server's code in this repo, or spawned from a published package / remote URL? Third-party → `Workflows/WrapExternalMcp.md`. |
| 2 | Where do tools register? | `grep -rn "registerTool(" <pkg>/src` — note whether reads and writes live in separate files. |
| 3 | What schema style? | Read the imports at the top of the registration file (this repo: `import * as z from 'zod/v4'`). |
| 4 | Is there a guardrail wrapper, and a coverage assertion that fails closed? | `grep -rn "withGuardrail\|verifyGuardrailCoverage\|RISK_CLASSIFICATIONS" <pkg>/src`. If a coverage check exists, find **how it enumerates registered tools** — a hardcoded list needs the new name too. |
| 5 | Is there a catalog / permission map something else consumes? | `grep -rn "TOOL_CATALOG\|PERMISSION_CATALOG" <pkg>/src ../gateway_mcp/src`. |
| 6 | Test layout and command? | `ls <pkg>/tests`, `jq .scripts <pkg>/package.json`. Find the test that asserts the registered set — extend it. |
| 7 | How does a client pick up the new tool? | Transport (`stdio` / `http`) and whether the host caches the tool list at connect. Almost always: reconnect required. |

## Recording the Answer

Write the derived shape to the session scratchpad as `shape-<server>.md` — a short table of
files to touch, in edit order, plus the verify command. It is a session cache, not a repo
artifact: never commit it, and re-derive it in a later session rather than trusting it.

## Fail-Closed Rules

These hold for any server, regardless of shape:

- Risk/permission metadata is written **before** the registration that depends on it.
- If a required permission has no app-only equivalent, the tool is **not registered** in app-only
  mode — an absent capability beats a tool that 403s on every call.
- If any touchpoint cannot be completed (no permission granted, no test possible), stop and report
  rather than landing a partial promotion. A partial promotion is a dead server, not a missing tool.
