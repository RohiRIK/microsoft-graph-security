# Microsoft 365 Security — agent plugin

Portable security-investigation workflows packaged once for **Claude Code**,
**Antigravity (`agy`)**, **Goose**, **Pi**, **OpenCode**, **OpenClaw**, and any
MCP-compatible agent.

**To use the workflows — paste this into your agent, one line:**

> Install the microsoft-graph-security plugin, then route my request through `skills/m365-security-workflows/SKILL.md` to the canonical skill for it; this is a read-only-by-default Microsoft 365 MCP suite where writes need an explicit `confirm: true`, and every answer must open by naming the tenant from `gateway://session`.

![One workflow package, many agents](plugins/microsoft-graph-security/assets/plugin-host-adapters.svg)

## Layout

| Path | Host |
|---|---|
| `plugins/microsoft-graph-security/` | Claude Code, Pi, Hermes (Agent Plugins v1) |
| `antigravity/microsoft-graph-security/` | Antigravity `agy` |
| `goose/m365-security-workflows.yaml` | Goose |

## Install — one line

> Before you install anything, read `INSTALL-AGENTS.md` in this repository, find the section for the agent you actually are, and follow exactly that — it carries the command, the verification, the rollback and the honest limits for all **47 hosts**, and it tells you plainly which ones you must not run.

## Safety

- **Read-only by default.** Write tools exist only when the backend runs with
  its write opt-in, and destructive/critical writes still need `confirm: true`.
- **Name the tenant first.** Every investigation opens by reading the gateway
  session resource and stating the tenant display name and GUID.
- **Never invent data.** No fabricated users, profiles, tenants, or results.
- **No secrets ship here.** No credentials, no tenant configuration, no
  personal data.

## Licence

MIT — see [LICENSE](LICENSE).
