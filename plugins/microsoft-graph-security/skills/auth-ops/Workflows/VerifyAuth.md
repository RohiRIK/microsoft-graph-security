# VerifyAuth

Prove auth works — without touching the tenant.

## Steps

1. **`bun run doctor`** first. Read-only, no browser, no writes. It reports per package:
   resolved tenant, access mode, credential source, and enabled/disabled state.
2. If a package says `not verified` (delegated), and you need reachability proven:
   **`bun run doctor --sign-in`**. One browser prompt, shared across every enabled plane.
   Say so before running it — an unexpected browser is the failure this repo already had.
3. Read the grant diff. Missing permissions name the tools they gate. Distinguish:
   - **not granted** → consent would fix it. Print the command; do not run it.
   - **unavailable in this mode** → app-only permission under delegated. Consent cannot fix it.
     `doctor` currently prints `ThreatAssessment.Read.All` as "not granted" under delegated —
     it is this case.
   - The notice that the token **also grants** write scopes is expected with `wellknown` (see
     SKILL.md Gotchas) — writes are still refused in code.
4. DLP uses its own sign-in, made by the first DLP job: `purview.start_dlp_export` (`days: 1`)
   proves it end to end — it reuses a current sign-in, or opens the browser inside the job
   (the operator answers it). `bun run cli purview dlp signin` does it ahead of time.
5. For MCP-level behaviour, drive the gateway over stdio (`skills/runtime-verification/`):
   `tools/list` and an **unconfirmed** `tools/call` on a write tool are auth-free and reach no
   tenant. The unconfirmed call returns the HITL preview — that is how you verify the guardrail.

## Never

- `confirm: true` on a write tool. It executes against whatever tenant is configured.
- Widening the allowlist or enabling writes to make a check pass. A refused start is the
  control working.

## Telemetry

```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"auth-ops","workflow":"VerifyAuth","status":"ok","duration_s":'$SECONDS'}' \
  >> ~/.claude/state/execution.jsonl
```
