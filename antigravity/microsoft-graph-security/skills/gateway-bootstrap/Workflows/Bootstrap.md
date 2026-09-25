# Bootstrap Workflow

One-time setup: creates the Entra ID app registration, grants admin consent, and provides configuration for `settings.yaml`.

## Prerequisites

- Bun installed (`bun --version`)
- An Entra ID tenant where you can create app registrations
- Port 7842 free (loopback redirect)

## Steps

```bash
cd gateway_mcp
bun install        # first time only
bun run bootstrap
```

Or via the CLI directly:
```bash
bun run src/cli.ts bootstrap
```

The script will:
1. Open a browser for interactive sign-in (MS Graph PowerShell client)
2. Check for existing `mcp-gateway` tagged app (idempotent)
3. Create app registration + service principal if new
4. Resolve appRole IDs at runtime from Microsoft Graph SP (never hardcoded)
5. Grant admin consent for derived scopes (read from backends' `PERMISSION_CATALOG`)
6. Provision certificate/keyring secret
7. Output the `settings.yaml` profile block with `tenantId` and `clientId`

Add `--writes` to enable write scopes:
```bash
bun run bootstrap --writes
```

## After bootstrap

```bash
bun run dev
```

## Verify bootstrap

```bash
bun run status --json | jq '.configured'
# should return: true
```

## Gotchas

- If the browser doesn't open, copy the URL from stdout and open manually.
- "Authentication flow blocked" = tenant has CA policy blocking device code. Interactive (loopback) is the primary path — this is expected.
- Bootstrap uses `common` tenant endpoint for the initial sign-in, then determines your tenant from the auth response.
- Re-running bootstrap reuses the existing app (tag `mcp-gateway`). It does NOT create duplicates.
