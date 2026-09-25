# Microsoft 365 Security — agent plugin

Portable security-investigation workflows packaged once for **Claude Code**,
**Antigravity (`agy`)**, **Goose**, **Pi**, **OpenCode**, **OpenClaw**, and any
MCP-compatible agent.

**To use the workflows — copy this into your agent:**

```text
Install the microsoft-graph-security plugin, route my request through skills/m365-security-workflows/SKILL.md to the canonical skill for it, and never improvise a procedure. This suite is read-only by default, writes need an explicit confirm: true, and every answer must open by naming the tenant from gateway://session.
```

![One workflow package, many agents](plugins/microsoft-graph-security/assets/plugin-host-adapters.svg)

## Layout

| Path | Host |
|---|---|
| `plugins/microsoft-graph-security/` | Claude Code, Pi, Hermes (Agent Plugins v1) |
| `antigravity/microsoft-graph-security/` | Antigravity `agy` |
| `goose/m365-security-workflows.yaml` | Goose |

## Quick install

Copy this one line into your agent:

```bash
claude plugin marketplace add RohiRIK/microsoft-graph-security && claude plugin install microsoft-graph-security@rohirik-m365-security
```

Not Claude Code? Open [`INSTALL-AGENTS.md`](INSTALL-AGENTS.md) and follow the section for the agent you are — 47 hosts, each with the command, the verification, the rollback, and the honest limits.

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
