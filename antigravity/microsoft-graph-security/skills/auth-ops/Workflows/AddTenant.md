# AddTenant

Onboarding a client tenant: a new profile, discovered by signing in.

## The rule that comes first

**The agent never runs this.** It opens a browser and authenticates a human
against a directory that belongs to someone else. Print the command and stop —
the same boundary as `bun run bootstrap` under refusal 4.

An agent that runs it does two things it must not: it initiates a sign-in nobody
asked for, and it decides which account answers. Only the operator can pick the
account, and picking the wrong one silently onboards the wrong company.

## The command

```bash
bun run profile add <name>
```

Signs in against `common`, reads the tenant off the account that answers, and
writes the profile from that. The GUID is an **output**, never an input — so it
cannot be mistyped, which is the failure the old hand-written flow invited.

`mcp-gateway profile init` is the same operation from inside the gateway
package, and writes the same file. Prefer the root command; they share one
implementation.

## What it will not do, and why you should not work around it

- **Never widens an allowlist.** The new profile is fail-closed to the one
  tenant just signed into. A second client is a second *profile* — refusal 2.
- **Never stores a credential.** Delegated by default, `clientId: wellknown`, so
  there is nothing to store. The discovery cache is revoked immediately after,
  because it is credential material for a tenant nothing is bound to.
- **Never grants consent.** Adding a client and being allowed into their data
  are different acts; this is only the first.
- **Refuses a tenant that already has a profile**, whatever it is called. Two
  names for one tenant is how you stop knowing which is live.
- **Writes are off** in the generated profile. Turning them on is refusal 3.

## After it runs

1. `bun run status --profile <name>` — confirm the tenant and that the allowlist
   says "this one only".
2. It is not live until `activeProfile` names it. If the pointer was already
   dangling at that name, the command says so and it is live immediately.
3. **Reconnect any running MCP client.** Settings resolve once at startup; a
   gateway already running stays on its old tenant. It will now refuse rather
   than serve the wrong one — see `gateway_mcp/src/staleness.ts` — but refusing
   is not the same as working.

## When it goes wrong

| What you see | What it means |
|---|---|
| `AADSTS90072` | The account picked does not exist in the tenant being signed into. Pick the right account, or you are onboarding the wrong company. |
| `Tenant … already has a profile` | Correct behaviour. Find the existing profile with `bun run status`. |
| `A profile called "x" already exists` | Names are unique. Nothing was signed into — this refuses before opening a browser. |
| `activeProfile "x" is not defined` | The pointer names a profile that was never created. This command is the fix, and it works despite the dangling pointer. |

## Removing one

By hand, and deliberately. Delete the block from `settings.yaml`; if it was the
active profile, repoint `activeProfile` first or every server refuses to start.

An unused profile is not inert — it is a client tenant a stale connection can
still be pointed at. Remove finished engagements rather than leaving them.
