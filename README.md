# Microsoft 365 Security — agent plugin

Portable security-investigation workflows packaged once for **Claude Code**,
**Antigravity (`agy`)**, **Goose**, **Pi**, **OpenCode**, **OpenClaw**, and any
MCP-compatible agent.

![One workflow package, many agents](assets/plugin-host-adapters.svg)

## Layout

| Path | Host |
|---|---|
| `plugins/microsoft-graph-security/` | Claude Code, Pi, Hermes (Agent Plugins v1) |
| `antigravity/microsoft-graph-security/` | Antigravity `agy` |
| `goose/m365-security-workflows.yaml` | Goose |

## Claude Code

```bash
claude plugin marketplace add RohiRIK/microsoft-graph-security
claude plugin install microsoft-graph-security@rohirik-m365-security
```

Load without installing:

```bash
claude --plugin-dir ./plugins/microsoft-graph-security
```

## Antigravity

```bash
agy plugin install ./antigravity/microsoft-graph-security
```

## Goose

```bash
export GOOSE_RECIPE_PATH="$PWD/goose"
goose recipe list
```

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
