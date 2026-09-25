# PromoteToTool

Turn a ToolSpec into a registered tool. Requires an explicit yes from the user; a write tool
requires a second yes of its own.

## Step 1: Gate

- Read consent present? No → stop, return to `DraftAdHocTool.md` Step 5.
- Write tool? Confirm separately, naming what it can mutate and under which risk level. A write
  tool is a new way to change the tenant — the read-tool yes does not cover it.
- Source editable? No → `WrapExternalMcp.md`.

## Step 2: Derive the Shape

Work through the 7 questions in `ShapeContract.md`. Start from `Adapters.md` Shape A for this
repo's packages, then verify the two load-bearing lines still hold:

```bash
grep -n "withGuardrail\|verifyGuardrailCoverage" <pkg>/src/tools/register.ts | head
```

## Step 3: Apply the Touchpoints, in Order

Shape A order (`Adapters.md` has the full table):

1. `src/guardrails/risk.ts` — classification first.
2. `src/tools/schema.ts` — only if a new shared fragment is genuinely needed.
3. `src/tools/register.ts` or `writeRegister.ts` — `registerTool(...)` wrapped in `withGuardrail(name, handler)`.
4. The coverage list in that same file — `ALWAYS_REGISTERED` or the `Set` in `verifyGuardrailCoverage()`.
5. `src/catalog.ts` — `TOOL_CATALOG` entry plus `PERMISSION_CATALOG` mapping.
6. `tests/tools/register.test.ts` — assert registration and the Graph path/query the handler builds.

Match the file's surrounding idiom exactly: field-projection const, `compactObject` +
`redactSensitiveValues`, `formatKeyValueRows`, `try/catch` returning `summarizeError`.

If the permission has no application equivalent, gate registration on access mode and thread the
same flag into the coverage check — do not register a tool that will 403 on every call.

Not a Graph call? Read *A tool that does not use Graph* and *Two limits every tool must respect*
in `Adapters.md` before writing the handler — role-based access stays out of
`PERMISSION_CATALOG`, and anything slower than 30 s is a background job.

## Step 4: Verify

While iterating, the package alone:

```bash
bun test <pkg>            # coverage check + the new unit test
bun run --cwd <pkg> lint  # Biome: noConsole in src/, 120 cols, single quotes
bun run --cwd <pkg> typecheck
```

Changed anything in `mcp_shared/`? Run `bun install` in **every** package first — it is a `file:`
dependency, copied at install time, so the packages keep the old code until reinstalled.

Then prove the server boots and lists the tool over stdio — the coverage check only fires at
startup, so a green unit test alone does not prove the server survives. The package's
`tests/server.smoke.test.ts` does this and asserts the tool list; update its expected tools.

```bash
bun run <pkg>/src/index.ts   # expect clean startup, no throw (loads settings.yaml / active profile)
bun run cli <plane> --help   # verify Unified Root CLI dispatcher for this plane
```

Finally the gate — CI does not run here (AGENTS.md → *Local Verification Is The Gate*):

```bash
bun run verify:local          # before committing
bun run verify:local --full   # before a PR; post the results table as a PR comment
```

## Step 5: Reconnect

The tool stays invisible until the MCP client re-connects — tool lists are fetched at connect.
Tell the user to reconnect (`/mcp`, or restart the session) and then call the namespaced name
(`mcp__m365__<namespace>_<tool>`) to confirm end-to-end.

## Step 6: Document

Describe the tool where the package is described — `README.md`, the package's `docs/`, and the
skill that will use it (its Quick Reference table). Do not add tool counts to prose: they drift
(the repo has corrected "9 tools" that were 15); the authoritative list is `risk.ts` plus the
coverage lists. A tool nobody documented is a tool nobody finds.

Report what changed as a short file list, and mention `RollbackToolChange.md` exists.

## Execution Log

```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"mcp-tool-forge","workflow":"PromoteToTool","status":"ok","duration_s":'$SECONDS'}' \
  >> ~/.claude/state/execution.jsonl
```
