# OpenClaw adapter

OpenClaw natively discovers workspace skills at `<workspace>/skills/<name>/SKILL.md` and project agent skills at `<workspace>/.agents/skills/<name>/SKILL.md`.

The safe local installer below is intentionally opt-in. It never edits `~/.openclaw/openclaw.json`, never installs globally, and refuses to replace an existing unrelated file.

```bash
bun run scripts/install-openclaw.ts --workspace "$PWD"
```

The installer links this repository's canonical `skills/` directory into the requested OpenClaw workspace. For an existing workspace skill with the same name, it leaves the file untouched and exits non-zero. Roll back with:

```bash
bun run scripts/install-openclaw.ts --workspace "$PWD" --uninstall
```

After installation, configure the gateway under OpenClaw's supported `mcp.servers` configuration. This repository does not write that user-level configuration automatically; the operator must add the local gateway command and review it.
