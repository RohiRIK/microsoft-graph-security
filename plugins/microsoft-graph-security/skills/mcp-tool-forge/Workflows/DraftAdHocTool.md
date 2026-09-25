# DraftAdHocTool

The gap moment: the user asked something no registered tool answers. Answer it anyway, then offer
the permanent version once.

## Step 1: Confirm the Gap Is Real

Search the registered surface before writing anything — `TOOL_CATALOG` in the candidate package,
and the live `mcp__m365__*` tool names. A tool that exists under a different name, or that is
unregistered only because of access mode (delegated-only permissions), is not a gap. Say which of
the two it is.

## Step 2: Write the Script in the Scratchpad

Before writing a custom probe script, check if an existing Unified Root CLI command already exposes the data:

```bash
bun run cli <plane> [command] [flags]
# or for cross-plane investigation:
bun run cli triage <user|app|offboard> <id>
```

If an ad-hoc probe is needed, you can scaffold a typed probe using the CLI:

```bash
bun run cli scaffold <plane> <name>
# generates probes/<plane>/<name>.ts using createProbeClient with automated profile binding
```

Or write a probe script in the session scratchpad directory (never a package root — untracked `dogfood-*.ts`
files at package roots are what this skill exists to stop).

Reuse the package's own building blocks and modern profile-aware config loader instead of re-implementing auth. `useProfile('<plane>')` resolves configuration and credentials from `settings.yaml` (or `~/.mcp-graph/profiles`):

```ts
import { useProfile } from 'mcp-shared/config';
import { createAuthProvider, loadConfig } from '<pkg>/src/config.ts';
import { GraphClient } from '<pkg>/src/graph/client.ts';

await useProfile('<plane>'); // 'entra' | 'intune' | 'defender' | 'exchange' | 'purview'
const config = await loadConfig();
const auth = await createAuthProvider(config);
const client = new GraphClient(config, auth);
```

Run it directly with Bun (settings are loaded automatically from `settings.yaml`):

```bash
bun run <scratchpad>/probe.ts
# or to test against a specific client profile:
bun run with-profile <profile> -- bun run <scratchpad>/probe.ts
```

If it 403s, the blocker is consent, not code — report the missing permission and stop. Do not
route around a permission with a different API.

**When the data is not in Graph** (confirm on Microsoft Learn first — DLP policies, for example,
are only in Security & Compliance PowerShell): a scratchpad `pwsh` probe, read-only by
construction — `Connect-IPPSSession -CommandName <only the Get-* cmdlets you need>`, assert the
connected tenant equals the profile's before reading, and write output to the scratchpad. The
operator answers its browser sign-in. Use the probe to learn the **real data shape** before
designing the tool; fields that look authoritative can be empty (every DLP rule kept its
conditions in `AdvancedRule`, not in the flat fields).

## Step 3: Answer the Question

Give the user their answer first, in the form they asked for. The promotion is secondary; a user
who only wanted the number should get the number.

## Step 4: Capture the ToolSpec

Record it inline in the reply (short), so promotion does not re-derive it:

```
ToolSpec
  name:        list_named_locations
  package:     entra_id_mcp        namespace: entra
  endpoint:    GET /identity/conditionalAccess/namedLocations
  inputs:      top, skip_token, select
  fields:      id, displayName, @odata.type, isTrusted, createdDateTime
  permission:  Policy.Read.All
  risk:        read_sensitive
  write:       no
```

Risk level follows the package's existing convention for that data class — copy the neighbouring
classification rather than inventing one.

## Step 5: Offer Once

Ask exactly once whether to promote it. Silence, a topic change, or a follow-up question is not
consent. If the answer is yes, go to `PromoteToTool.md`. If no, leave the script in the scratchpad
and say so — it disappears with the session.

## Execution Log

```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"mcp-tool-forge","workflow":"DraftAdHocTool","status":"ok","duration_s":'$SECONDS'}' \
  >> ~/.claude/state/execution.jsonl
```
