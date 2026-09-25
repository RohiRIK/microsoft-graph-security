# Goose adapter

Goose has **no `SKILL.md` recipe format of its own**, but it does support Agent
Skills natively (`goose skills list`) *and* its own **Recipe** format
(`goose recipe validate`). This adapter ships the recipe as a routed entry
point; the skills come from the canonical `skills/`.

## The zero-install path (already working here)

Goose reads Agent Skills from `~/.claude/skills/` and from project
`.agents/skills/`. This repository already links
`.agents/skills -> ../skills`, so `goose skills list` already reports all 19
canonical skills. Nothing to install:

```bash
goose skills list | grep cloud-security-engineer
```

## The recipe

A recipe is Goose's own reusable-workflow format: a YAML file (`.yaml` — the
CLI does **not** support `.yml`) or JSON with a schema of
`version / title / description / instructions / prompt / activities /
parameters / extensions / settings`.

`m365-security-workflows.yaml` is a thin router: its instructions point at the
canonical skills and repeat the non-negotiable safety gates (name the tenant,
read-only by default, `confirm: true` for writes, never invent data). It does
not duplicate any workflow procedure.

## Validate

```bash
goose recipe validate ./plugin/adapters/goose/m365-security-workflows.yaml
```

Expected: `✓ recipe file is valid`

## Load it

Goose discovers recipes from the current directory, from directories named by
`GOOSE_RECIPE_PATH`, or from a GitHub repo via `GOOSE_RECIPE_GITHUB_REPO`.

```bash
export GOOSE_RECIPE_PATH="$PWD/plugin/adapters/goose"
goose recipe list --format json          # discoverable
goose run --recipe m365-security-workflows --text "Triage <user>"
goose run --recipe m365-security-workflows \
  --params user_or_device="user@client.com" --text "triage"
```

In goose Desktop the recipe appears in the Recipes sidebar; you can also assign
a `/slash-command` to it.

## MCP

Goose configures MCP servers as **extensions** in
`~/.config/goose/config.yaml` (user-level). This repository does not write that
file. The plugin's `mcp_config.json` uses the same
`{"mcpServers": {...}}` shape and is documented in the generic MCP adapter;
copy the gateway entry into your own config after review.

## Rollback

Nothing is installed by the repo. To stop using the recipe, unset
`GOOSE_RECIPE_PATH` or delete `m365-security-workflows.yaml` from wherever you
copied it.
