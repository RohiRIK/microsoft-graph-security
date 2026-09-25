# OpenCode adapter

OpenCode has native project skills and project MCP configuration. **Nothing to
install** — the repo already links `.opencode/skills`, `.claude/skills` and
`.agents/skills` to the canonical `skills/`.

```bash
bun run scripts/link-skills.ts
```

## Validate (read-only)

```bash
opencode debug config          # resolved configuration
opencode debug skill           # every discovered skill + its resolved location
```

`opencode debug skill` is the authoritative check. It prints JSON, so count
entries whose `location` points at this repo rather than grepping for a skill
name — the bodies are inlined, so a naive grep can miss. On this machine it
resolves 19 repo skills.

## MCP

This project already declares a local `mg` server in the OpenCode config. For
another project, add the gateway to `opencode.json` / `opencode.jsonc`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "microsoft-graph": {
      "type": "local",
      "command": ["bun", "run", "gateway_mcp/src/index.ts"],
      "enabled": true
    }
  }
}
```

`command` is an array of strings (never a bare string), `type` is required, and
a relative path only resolves while the workspace *is* this repo. No global
OpenCode configuration is changed by this repository.
