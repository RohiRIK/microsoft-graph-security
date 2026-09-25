# ChangeScopes

Add or remove a Graph permission.

## Steps

1. **Verify the scope exists in the form you need.** Microsoft's permissions reference:
   a `-` in the **Delegated** column means app-only. Adding one anyway makes Entra reject the
   entire sign-in, not just that scope. See `ScopeRules.md`.
2. **Add it in two places or not at all:** `DELEGATED_READ_SCOPES` in `<pkg>/src/config.ts`
   *and* `PERMISSION_CATALOG` in `<pkg>/src/catalog.ts`, mapped to the tools that need it.
   `tests/least-privilege.test.ts` fails if a requested scope has no registered tool.
3. **App-only-only scopes** go in `APP_ONLY_READ_SCOPES`, never the delegated list.
4. `bun run test` — the least-privilege test is the gate; then `bun run verify:local` before
   committing (CI does not run).
5. `bun run doctor --sign-in` — reports the new scope as not granted until consent.
6. **Print the consent step for the operator.** Do not grant it.

## Removing

Always safe to propose. An ungranted scope is a 403 on one tool; an over-granted one is
standing access to a client's data. If no registered tool needs it, remove it.

## Never

- Add a scope "to be safe" or to unblock an unrelated failure.
- Grant consent, or instruct a tool to grant it.

## Telemetry

```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"auth-ops","workflow":"ChangeScopes","status":"ok","duration_s":'$SECONDS'}' \
  >> ~/.claude/state/execution.jsonl
```
