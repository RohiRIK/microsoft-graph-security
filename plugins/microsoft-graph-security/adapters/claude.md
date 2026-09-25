# Claude Code adapter

The package is a Claude Code plugin: `.claude-plugin/plugin.json` plus `skills/`.
Claude Code loads it natively — no install required.

## Use the built package, not the source dir

`./plugin` is the **source**: one routing skill plus the adapters. The portable
artifact is `dist/portable-plugin/`, which carries all 20 skills (19 canonical
+ the router). Installing `./plugin` directly gives you the router with none of
its targets, so the router's names would resolve to nothing.

```bash
bun run build:portable-plugin
```

## Validate (read-only, writes nothing)

```bash
claude plugin validate ./dist/portable-plugin --strict
```

## One-command local load — no install

`--plugin-dir` is a top-level `claude` flag (it is *not* a subcommand flag, so
`claude plugin details --plugin-dir` fails):

```bash
claude --plugin-dir ./dist/portable-plugin
```

Confirm what actually loaded:

```bash
claude --plugin-dir ./dist/portable-plugin \
  plugin details microsoft-graph-security
```

Expected:

```
Skills (20)  analyze-configuration, app-governer, auth-ops, ...
Projected token cost
  Always-on:   ~1.2k tok   added to every session
```

## The zero-install path

Claude Code reads project `.claude/skills/`, and this repo already links
`.claude/skills -> ../skills`, so all 19 canonical skills are already available
without the plugin at all. Add the plugin only when you want these skills in
*other* projects.

## Install (optional, operator choice)

```bash
claude plugin install ./dist/portable-plugin --scope local
```

Scopes: `user` (every project on this machine), `project` (committed
`.claude/settings.json`, affects collaborators), `local` (this repo only,
gitignored). This repository does not run an installer or touch user-level
settings.

Rollback:

```bash
claude plugin uninstall microsoft-graph-security
```
