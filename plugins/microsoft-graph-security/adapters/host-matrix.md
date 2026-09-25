# Host support matrix

One canonical workflow source (`skills/`), thin adapters, MCP as the universal
fallback. "Zero-install" means the host already reads this repo's
`.agents/skills` symlink, so nothing has to be installed to get the 19 skills.

| Host | Native skills? | Native package/format | Needs | Verified here |
|---|---|---|---|---|
| **Antigravity (`agy` v1.2.11)** | yes — `.agents/skills` default | `plugin.json` (+ `mcp_config.json`) | nothing (zero-install) | `agy plugin validate` → 20 skills |
| **Claude Code (2.1.272)** | yes — `.claude/skills` | `.claude-plugin/plugin.json` | nothing (`--plugin-dir`) | `plugin validate --strict` → 20 skills |
| **Goose (1.45.0)** | yes — reads `.agents/skills`, `~/.claude/skills` | Recipe (`.yaml`) | nothing (zero-install) | `goose recipe validate`; `goose skills list` → 19 |
| **Hermes Agent** | yes — Agent Plugins v1 `skills/` | `plugin.json` (Agent Plugins v1) | nothing | `plugins validate` + `doctor` pass |
| **OpenCode (1.18.32)** | yes — `.opencode/skills`, `.claude/skills`, `.agents/skills` | `opencode.json` MCP | nothing (zero-install) | `opencode debug skill` → 19 |
| **Pi (0.87.1)** | yes — `pi.skills` | `package.json` (`pi.skills`) | `-e ./plugin` | manifest + resources resolve; **runtime blocked** (see below) |
| **OpenClaw** | yes — `<workspace>/skills`, `.agents/skills` | `mcp.servers` in config | optional local link | installer idempotent + collision-safe; **CLI not installed** |
| ~~Gemini CLI~~ | — | — | — | **REMOVED** — deprecated; superseded by Antigravity, which replaces it |
| **Zed, Cursor, Cline, Codex, Crush, Aider** | no native package | MCP only | host MCP config | not tested; MCP-only per docs |

For the MCP-only rows, copy the gateway entry from
`plugin/adapters/mcp.md` into that host's MCP settings. Do not invent a
manifest for a host you have not read the docs for.

## The universal interop point

Five hosts read `.agents/skills/` (Agent Skills open standard): Antigravity,
Goose, Pi, OpenCode, OpenClaw — and Claude Code via the sibling
`.claude/skills` link. This repo already links all three paths at `../skills`,
so those hosts see the same 19 skills with **no install**. That link is the
single highest-leverage piece of the whole adapter set — recreating it is what
`bun run link-skills` does.

## Known-broken on this machine

- **Gemini CLI** refuses to authenticate: `IneligibleTierError — This client is
  no longer supported for Gemini Code Assist for individuals … migrate to the
  Antigravity suite`. It cannot list or load skills, so it is not a usable host
  here. Antigravity is its successor.
- **Pi** loads packages but any run that reaches a model returns
  `You're out of extra usage`. Manifest and resources resolve; runtime load is
  unproven.
- **OpenClaw** is not installed, so `openclaw mcp doctor` was never run.
- **Gemini CLI is removed from this project** — deprecated, and its own error
  points users at Antigravity, which is supported instead.

## What "validated" means

- **Statically validated**: manifests/resources parse, frontmatter conforms,
  and any host CLI that can validate without side effects was run.
- **Runtime loaded**: a host actually started and listed the package/skills.
- **Interactive**: needs a browser/UI, so an operator must confirm.

A passing validator is **not** proof a host loaded the package. We do not claim
a host works just because its files parse.
