# mcp-tool-forge — Known Shapes

Shapes already derived, per `ShapeContract.md`. Re-verify before editing; these drift.

## Shape A — Graph backend packages in this repo

Applies to `entra_id_mcp`, `intune_mcp`, `exchange_online_mcp`, `defender_mcp`, `purview_mcp`.
Six touchpoints, in this order:

| # | File | Edit |
|---|------|------|
| 1 | `<pkg>/src/guardrails/risk.ts` | `RISK_CLASSIFICATIONS` entry: `level`, `requiredPermissions`, `description`, `requiresConfirmation`, `warning` for sensitive reads. **First** — everything else depends on it. |
| 2 | `<pkg>/src/tools/schema.ts` | Only if the tool needs a new shared fragment. Reuse `paginationSchema`, `optionalSelect`, `graphObjectPath`, `escapeODataString`, `validateIsoDateTime`. |
| 3 | `<pkg>/src/tools/register.ts` (read) or `writeRegister.ts` (write) | `server.registerTool(name, {title, description, inputSchema}, withGuardrail(name, handler))`. |
| 4 | same file, the coverage list | Add the name to `ALWAYS_REGISTERED` (purview/newer packages) or the `Set` inside `verifyGuardrailCoverage()` (entra). A conditionally registered tool goes in its own list, gated by the same flag (purview: `RECORDS_MANAGEMENT_TOOLS`, `DLP_TOOLS`, `DLP_EXPORT_TOOLS`). **Skipping this silently disables the check for the new tool.** |
| 5 | `<pkg>/src/catalog.ts` | `TOOL_CATALOG` group entry (`{ name, riskLevel, write? }`) **and** `PERMISSION_CATALOG` least-privilege mapping. |
| 6 | `<pkg>/tests/tools/register.test.ts` | Extend the stub-client test: assert the tool registers and that it produces the expected Graph path/query. Stub client records `{path, query}` — no network. |

### Handler conventions

- `client.list(path, query, top)` returns `{ items, nextLink }`; `client.get(path, query)` returns the object.
- Project fields with `compactObject(redactSensitiveValues(item), FIELDS)` and a `FIELDS` const — never dump raw Graph objects.
- Text output via `formatKeyValueRows(rows, [...])`; also return `structuredContent`.
- Wrap the body in `try/catch` and return `summarizeError(error)` as text — do not throw out of a handler.
- Never interpolate free text into `$filter`. Closed zod enums, or `escapeODataString`.

### Write tools (extra requirements)

- File is `writeRegister.ts`; registration is behind the package's `<PREFIX>_ENABLE_WRITES` config flag.
- Risk level `write_standard` | `write_destructive` | `write_critical`; the last two set
  `requiresConfirmation: true`, and `withGuardrail` then enforces the two-phase preview
  (`guardrails/hitl.ts`) — first call without `confirm: true` returns a preview, never executes.
- Spread `destructiveSchema` into the input schema for `confirm` + `reason`.
- Add `write: true` to the `TOOL_CATALOG` entry, and list the action in `SECURITY_GUARDRAILS.gated_write_actions`.

### Gateway propagation

`gateway_mcp/src/backends/catalogs.ts` imports each package's `PERMISSION_CATALOG`, and
`backends/proxy.ts` aggregates the live tool list at connect — so touchpoint 5 is all the gateway
needs. Two caveats: a raw tool name that collides with another backend gets prefixed differently
(`findCollisions` in `backends/namespace.ts`), and the gateway must be restarted to re-connect
backends.

### Access-mode gating precedent

`purview_mcp` registers the retention-label tools only under delegated auth
(`registerRecordsManagement` argument), and the DLP export tools only when a Security &
Compliance sign-in exists (`dlp.compliance`). Both flags are threaded into
`verifyGuardrailCoverage(includeRecordsManagement, includeDlp, includeDlpExport)`. Copy that
pattern whenever a tool cannot work in some mode: the flag controls registration and the
coverage check together, so the two never disagree.

### A tool that does not use Graph (the DLP precedent)

Some data has no Graph API — DLP configuration lives only in Security & Compliance PowerShell.
Such a tool still lives in the package and still takes all six touchpoints, with these
differences (`purview_mcp/src/dlp/`, `src/tools/dlp.ts`):

- **Own module, own registrar.** Logic in `src/<area>/` (pure, unit-tested); tools in
  `src/tools/<area>.ts` with `register<Area>Tools(server, deps)`, called from the package's
  `register*Tools`. Inject every side effect through `deps` (auth, runner, storage dir) so tests
  need no network, browser or PowerShell.
- **A role is not a scope.** When access comes from an admin role (e.g. *View-Only DLP Compliance
  Management*), `requiredPermissions: []` and **no `PERMISSION_CATALOG` entry** — anything in the
  catalog is requested at sign-in, and one invalid scope fails the whole sign-in. Name the role
  in the tool description instead.
- **Fixed script, validated inputs.** If a subprocess is needed (`pwsh`), the script is fixed
  text in the repo, only validated values are passed as arguments, and tokens travel in the
  child's environment, never on its command line. `src/dlp/pwsh.ts` runs them.
- **A write that bypasses the API clients checks writes itself.** `assertWritesEnabled` lives in
  `GraphClient.write`; a PowerShell write never reaches it. `create_dlp_policy` calls it explicitly,
  runs a separate script whose `-CommandName` list has no `Set-`/generic cmdlets, and sends only a
  plan the user was shown (plan id + hash) — the precedent for any non-Graph write.

### Two limits every tool must respect

- **30 seconds per call.** The gateway gives up on a backend call after 30 s. Anything slower
  (a 30-day DLP export took 14–17 minutes) becomes a **background job**: `start_<x>` returns a
  job id at once, `<x>_status` reports progress and the result (`src/dlp/jobs.ts`). One job at a
  time; jobs live in the server process, so a reconnect forgets them — say so in the status text.
- **Response size.** A 61,666-character result was too large for the client to take back in one
  call. Cap list output (`max_findings`-style parameter with a default, plus an
  `omitted…` count and how to get the rest) and make heavy detail opt-in (`include_coverage`).
  Measure the response on real data before shipping — fixtures are always small.

## Shape B — a plain MCP SDK server (no guardrails)

A single-file server built on `@modelcontextprotocol/server` with `StdioServerTransport`. One
touchpoint: `server.registerTool(...)`. No risk file, no catalog, no coverage check. Used for
sidecars produced by `WrapExternalMcp`. Promote to Shape A the moment the sidecar becomes durable
or gains a write path.

## Shape C — third-party MCP (not editable)

Notion, Gmail, Microsoft Learn, any remote HTTP MCP. No touchpoints — the source is not ours.
Route to `Workflows/WrapExternalMcp.md`. `LEARN_CATALOG` in `gateway_mcp/src/backends/catalogs.ts`
is the precedent for registering a backend that has no Graph permission at all.
