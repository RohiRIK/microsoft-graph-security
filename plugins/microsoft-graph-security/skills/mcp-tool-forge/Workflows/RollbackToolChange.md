# RollbackToolChange

A half-applied promotion does not degrade one tool — it stops the server booting, which removes
every tool in that package. Roll back fast, diagnose after.

## Step 1: Read the Failure

The two common startup failures name themselves:

- `Guardrail coverage check failed. Tools registered without a risk classification: <name>` —
  touchpoint 1 or 4 missing. Fixing forward is usually one line; do that instead of reverting.
- A type or import error — Biome/tsc will locate it.

Quote the decisive line to the user, not the whole trace.

## Step 2: See Exactly What Landed

Scope the diff to the touchpoints, not the whole tree:

```bash
git diff --stat -- <pkg>/src/guardrails/risk.ts <pkg>/src/tools <pkg>/src/catalog.ts <pkg>/tests
```

Other work in progress lives in the same tree — the repo commonly has many modified files. Never
`git checkout .` or `git stash` the whole working tree to undo one tool.

## Step 3: Revert or Fix Forward

Fix forward when the gap is a missing entry (usually the coverage list). Revert when the tool
itself was wrong:

```bash
git checkout -- <only the files this promotion touched>
```

If the promotion was already committed, `git revert <sha>` — do not rewrite history.

## Step 4: Prove the Server Boots

```bash
bun run <pkg>/src/index.ts   # clean startup, no throw (loads settings.yaml / active profile)
bun test <pkg>
bun run verify:local         # the gate, before committing the rollback
```

Then have the user reconnect the MCP client so its tool list matches reality again — a stale list
advertising a tool that no longer registers fails at call time.

## Step 5: Record the Lesson

If the failure was a shape the skill did not know about, add it to `SKILL.md` `## Gotchas` and, if
the contract itself changed, to `Adapters.md`. Gotchas accumulate — that is the point of them.

## Execution Log

```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"mcp-tool-forge","workflow":"RollbackToolChange","status":"ok","duration_s":'$SECONDS'}' \
  >> ~/.claude/state/execution.jsonl
```
