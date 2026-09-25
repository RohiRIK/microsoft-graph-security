# Portable Microsoft 365 security workflows

This package is the host-neutral workflow package for this repository. The substantive instructions stay in the repository's canonical `skills/`; host adapters only route to them and describe the host's supported native package or MCP format.

## Source vs built package

`./plugin` is the **source**: one routing skill, the adapters, and the
references. It is not portable on its own — the router names skills that only
exist in the repo root. The distributable is built:

```bash
bun run build:portable-plugin
```

- `dist/portable-plugin/` — Agent Plugins v1, Claude Code, Pi (20 skills)
- `dist/antigravity-plugin/` — Antigravity-native `plugin.json` (20 skills)

Both copy the canonical `skills/`; neither is checked in.

## Install and load

No global installation is performed by this repository. Choose one host:

```bash
# Antigravity CLI (agy)
agy plugin validate ./plugin/adapters/antigravity

# Hermes Agent (Agent Plugins v1)
hermes plugins validate ./plugin
hermes plugins doctor ./plugin

# Goose
goose recipe validate ./plugin/adapters/goose/m365-security-workflows.yaml

# Claude Code
claude plugin validate ./plugin --strict

# OpenCode: link the canonical skills into this project
bun run scripts/link-skills.ts

# OpenClaw: local, opt-in workspace skill link; refuses collisions
bun run scripts/install-openclaw.ts --workspace "$PWD"

# Pi: one invocation, no settings write
pi --no-session --no-approve --print --no-tools -e ./plugin "List the Microsoft 365 security workflows."
```

The first three commands validate; they do not install. Use the host's own reviewed install flow only after validation. For OpenClaw and OpenCode, configure the gateway separately using the host's MCP format; this package never changes user-level configuration.

## Zero-install hosts

Five hosts read `.agents/skills/` — Antigravity, Goose, Pi, OpenCode,
OpenClaw — plus Claude Code via `.claude/skills`. This repo links all of them
at `../skills`, so they discover the 19 canonical skills with nothing
installed. Run `bun run link-skills` after a fresh clone to restore the links.

## Host support

See `adapters/host-matrix.md` for every supported host, which need a package,
which are MCP-only, and which are broken on this machine.

## Rollback

```bash
# OpenClaw local link
bun run scripts/install-openclaw.ts --workspace "$PWD" --uninstall

# OpenCode/Claude project links
rm .opencode/skills .claude/skills .agents/skills
```

Pi's one-invocation `-e` form requires no rollback. Host package installation, if performed, must be removed with that host's own uninstall command.

## Validation and limits

- The focused integration tests are `bun test scripts/tests/portable-plugin.test.ts`.
- The project suite is `bun run test`; root script tests are `bun run test:scripts`.
- Gateway startup from the repository root and nested package directories is covered by the existing real-stdio smoke tests in `gateway_mcp/tests/server.smoke.test.ts` and each backend's `tests/server.smoke.test.ts`.
- Typecheck is `bun run typecheck`.
- Secret scan is `bun run scan`.
- `git diff --check` checks whitespace.
- Host-native validation is available above; OpenClaw is not installed in this environment, so its runtime doctor cannot be run here.
- Parsing a manifest is not proof that a host loaded it. Runtime MCP startup and interactive host verification remain operator actions.

See `adapters/` for the supported host formats and `references/runtime-and-safety.md` for the non-negotiable safety contract.
