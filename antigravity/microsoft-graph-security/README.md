# Antigravity (`agy`) adapter

Antigravity has a native plugin format, and the CLI ships a validator. This
directory holds an **Antigravity-native** manifest rather than reusing the
Agent Plugins v1 one, because the two schemas disagree.

## Why a second manifest

| | Agent Plugins v1 (Hermes) | Antigravity |
|---|---|---|
| `$schema` | `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json` | `https://antigravity.google/schemas/v1/plugin.json` |
| Allowed keys | `$schema, name, version, description, author, homepage, repository, license, keywords, extensions` | `name, description` only |
| Extra keys | allowed | **rejected** (`additionalProperties: false`) |

One file cannot satisfy both strict schemas, because `$schema` is a `const` in
the Agent Plugins v1 schema and a different URL here. So this adapter ships the
minimal Antigravity manifest, which is also a valid Agent Plugins v1 manifest
minus its `$schema` requirement. `plugin/plugin.json` stays the Hermes/Claude/Pi
one; this one is for Antigravity only.

## Directory shape Antigravity expects

```
<plugin>/
├── plugin.json          # required
├── mcp_config.json      # optional MCP servers
├── hooks.json           # optional
├── skills/<name>/SKILL.md
├── agents/<name>.md
└── rules/<name>.md
```

`mcp_config.json` uses a single `mcpServers` object. A stdio server needs
`command`; `args`, `env`, and `cwd` are optional. Remote servers use
`serverUrl` plus optional `headers`.

## Validate

Read-only; writes nothing:

```bash
# The adapter directory on its own (skills land at build time)
agy plugin validate ./plugin/adapters/antigravity

# The built package
bun run build:portable-plugin
agy plugin validate ./dist/antigravity-plugin
```

Expected for the built package:

```
✔ skills      : 20 processed
```

(19 canonical skills plus the portable routing skill.)

## MCP is deliberately NOT bundled

An earlier version of this adapter shipped an `mcp_config.json` pointing at
`gateway_mcp/src/index.ts`. It was removed because it cannot work from a global
install: the plugin lands in `~/.gemini/config/plugins/`, so a repo-relative
path resolves to nothing and the server dies with `Module not found`. The only
alternatives were a machine-specific absolute path (which we refuse to commit)
or a ~69 MB compiled binary (which `bun run build:plugin` already produces
separately). Shipping a config that silently fails is worse than shipping none.

The plugin therefore delivers **skills only**. Wire the gateway yourself, from a
directory where the relative path is true:

```bash
# Workspace level — this repo's documented Antigravity location:
# .agents/mcp_config.json
{
  "mcpServers": {
    "microsoft-graph": {
      "command": "bun",
      "args": ["run", "gateway_mcp/src/index.ts"]
    }
  }
}
```

Or globally at `~/.gemini/config/mcp_config.json`, where you choose the path and
own the consequence. `agy mcp list` confirms it afterwards.

Note: this repo gitignores `.agents/` wholesale, so no workspace
`mcp_config.json` can be committed here. It is an operator step by design.

## Install

These write to your profile and are **not** run by this repository. Note the CLI
stages into `~/.gemini/config/plugins/` — the path the docs call "global", not
the `~/.gemini/antigravity-cli/plugins/` path the same page also claims.
Verified on `agy` 1.2.11:

```bash
agy plugin install ./dist/antigravity-plugin
agy plugin list          # confirms the import and which components loaded
```

Rollback:

```bash
agy plugin uninstall microsoft-graph-security
agy plugin disable microsoft-graph-security   # toggle without removing
```

## The zero-install path

Antigravity defaults to `.agents/skills/`, and this repository already links
`.agents/skills -> ../skills`. So inside this repo, `agy` already discovers all
19 canonical skills with no install at all — the plugin only matters when you
want those skills in *other* projects.

## Safety

The plugin carries no credentials, no tenant, and no absolute paths. The gateway
keeps the existing rules: read-only by default, writes need opt-in **and**
`confirm: true`, and every investigation names its tenant first.
