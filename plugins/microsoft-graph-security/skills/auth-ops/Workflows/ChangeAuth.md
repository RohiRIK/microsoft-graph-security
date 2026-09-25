# ChangeAuth

Change access mode, add a profile, or move a client to app-only.

## Steps

1. **Scope the change to one profile.** A new client is a new profile, never a tenant appended
   to an existing allowlist. `bun run profile add <name>` discovers the tenant by signing in (see AddTenant), so
   a mistyped GUID cannot reach a fail-closed allowlist. Name is optional — omitted, it's
   derived from the tenant's own display name (`GET /organization`, slugified) after sign-in;
   pass one explicitly to override, or when using `--tenant <guid>` to skip sign-in (name is
   required in that case — nothing was signed into to derive it from).
2. **Choose the path deliberately** (`AuthModel.md`):
   - delegated + `wellknown` — no registration, no consent, ready now
   - app-only — required for unattended runs; can reach app-only-only planes
3. **Enable only the planes needed.** `enabled: false` per package means it is neither spawned
   nor consented for. Identity-only work asks for 12 permissions instead of 28.
4. **App-only ⇒ certificate.** `bun run bootstrap` generates and uploads one. Use `--secret`
   only if the operator explicitly asks; a secret is a bearer credential with a 180-day life.
   If a secret is unavoidable, it goes to the keyring via `profile set-secret` — stdin, never
   argv, never a file.
5. **Consent is the operator's.** Print the URL or command and stop.
6. `bun run doctor` to confirm. App-only should verify with no browser at all.

## Never

- Widen `tenant.allowlist` — add a profile instead.
- Set `enableWrites: true` in tracked settings.
- Write a secret into `settings.yaml`, `.env`, or any file. The loader rejects it for a reason.

## Telemetry

```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"auth-ops","workflow":"ChangeAuth","status":"ok","duration_s":'$SECONDS'}' \
  >> ~/.claude/state/execution.jsonl
```
