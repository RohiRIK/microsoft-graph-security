# Runtime and safety

## MCP entry point

The portable package contains instructions, not credentials or a tenant. Configure the host's MCP client separately with the repository gateway or the packaged binary.

The repository's development configuration is `.mcp.json`; a packaged Agent Plugin uses `mcp.json` and a plugin-relative executable. A host adapter must not embed an absolute path, tenant GUID, token, secret, or user-specific setting.

## Human gates

Keep the repository's existing behavior:

1. Read tools do not require write opt-in, but may require delegated sign-in and appropriate Graph permissions.
2. Write tools are registered only when the relevant package write flag is enabled.
3. Destructive and critical tools return a preview without `confirm: true`.
4. Show that preview to the human and obtain explicit approval before repeating the call with `confirm: true`.
5. Never infer approval from a request to investigate, triage, or prepare a plan.

## Tenant identity

Every investigation starts with `gateway://session` or the host's equivalent session resource. The response must name the tenant display name and GUID. If that resource is unavailable, say so; do not guess.

## Data handling

Keep secrets, tokens, credentials, tenant configuration, and personal data out of the package. Use redacted output. A report containing personal data belongs outside the repository and follows the repository's `bun run investigate` rules.
