# Install — instructions for AI agents

**You are reading this because a human pasted one line into you.** Your job is
to find the section for the agent you actually are, run exactly that, verify
it, and stop. Do not improvise a different approach, and do not install for a
host you are not.

If none of the sections match you, you are an **MCP client** — see Part 3.

---

## The safety contract (applies to every host, every skill)

Read this once; it is not repeated per host.

1. **Name the tenant first.** Every investigation opens by reading the gateway
   session resource (`gateway://session`) and stating the tenant display name
   and GUID. If it is unavailable, say so. Never invent a tenant, user,
   profile, or result.
2. **Read-only by default.** Write tools are registered only when the backend
   runs with its write opt-in enabled.
3. **Writes need a human.** Destructive and critical writes return a preview
   without `confirm: true`. Show it to the person, get explicit approval, then
   re-call with `confirm: true`. Never infer approval from "investigate" or
   "make a plan".
4. **Route, do not improvise.** Load `m365-security-workflows` and let it point
   you at the canonical skill. Do not restate or reconstruct a procedure.
5. **No secrets.** This package contains no credentials, no tenant
   configuration, and no personal data. If you find any, stop and report it.

---

## How confident is each entry?

| Mark | Meaning |
|---|---|
| ✅ | Verified on this machine — the command was actually run |
| 📄 | Vendor-documented — taken from that host's official docs, not run here |
| ❓ | Could not verify — no working documentation found. Treat as a lead, not an instruction |

**Do not run a ❓ command.** If you can only find a ❓ entry, use Part 3.

---

# Part 1 — Hosts with native Agent Skills

These read `SKILL.md` natively. That is the ideal case: the workflow loads
itself when the task matches.

---

## 1. Claude Code ✅

**How it works:** Claude Code is a plugin host. A plugin is a directory with
`.claude-plugin/plugin.json` plus `skills/`. It can also carry commands, agents
and hooks, though this package uses only skills.

**Install (from this repository, once):**

```bash
claude plugin marketplace add RohiRIK/microsoft-graph-security
claude plugin install microsoft-graph-security@rohirik-m365-security
```

**Try it with nothing installed** — useful when you do not want to touch the
user's plugin list:

```bash
claude --plugin-dir ./plugins/microsoft-graph-security
```

**Verify:**

```bash
claude --plugin-dir ./plugins/microsoft-graph-security \
  plugin details microsoft-graph-security
```

Expect `Skills (20)`. Note the cost line: roughly **3.4k tokens are added to
every session** while the plugin is enabled, whether or not you use a skill.
Report that to the human before installing.

**Rollback:**

```bash
claude plugin uninstall microsoft-graph-security --scope local
claude plugin marketplace remove rohirik-m365-security
```

**Trap:** `--plugin-dir` is a top-level `claude` flag. `claude plugin details
--plugin-dir ...` fails with `unknown option`.

---

## 2. Antigravity (`agy`) ✅

**How it works:** Google's Antigravity. A plugin is a directory with a
`plugin.json` manifest, optionally `mcp_config.json`, plus `skills/`, `agents/`,
`rules/` and `hooks.json`.

**Its schema is strict:** `additionalProperties: false`, accepting only `name`
and `description`, under its own `$schema`. That is why this repository ships
a separate Antigravity manifest rather than reusing the Agent Plugins v1 one.

**Install:**

```bash
agy plugin install ./antigravity/microsoft-graph-security
```

**Verify:**

```bash
agy plugin list
agy plugin validate ./antigravity/microsoft-graph-security
```

Expect `skills : 20 processed` and an entry with components `skills`.

**Rollback:**

```bash
agy plugin uninstall microsoft-graph-security
agy plugin disable microsoft-graph-security   # toggle without removing
```

**Two limits to tell the human about:**

- **There is no Antigravity marketplace.** `agy plugin link <mp> <target>`
  requires an already-registered marketplace, there is no `agy marketplace
  add`, and no marketplace key exists in its settings. Plugin install from a
  path is the only route.
- On `agy` 1.2.11 the CLI stages into `~/.gemini/config/plugins/`, **not** the
  `~/.gemini/antigravity-cli/plugins/` path the docs also claim.

---

## 3. Goose ✅

**How it works:** Goose supports Agent Skills *and* has its own **Recipe**
format. The recipe is a YAML entry point; the skills come from
`.agents/skills`.

**Already done for you:** if `.agents/skills` already points at the canonical
skills, `goose skills list` shows them and there is nothing to install.

**Install the recipe:**

```bash
export GOOSE_RECIPE_PATH="$PWD/goose"
goose recipe list
```

**Verify:**

```bash
goose recipe validate ./goose/m365-security-workflows.yaml
goose skills list
```

**Run it:**

```bash
goose run --recipe m365-security-workflows --text "Triage <user>"
```

**Rollback:** unset `GOOSE_RECIPE_PATH`, or delete the recipe file.

**Trap:** the filename must be `.yaml`. **Goose rejects `.yml`.**

---

## 4. Hermes Agent ✅

**How it works:** Hermes consumes Agent Plugins v1. The root `plugin.json` is
the manifest; `skills/` are discovered from it. Portable packages install
**disabled** by design, so enabling is a separate step.

**Install:**

```bash
hermes plugins install ./plugins/microsoft-graph-security
hermes plugins enable microsoft-graph-security
```

**Verify:**

```bash
hermes plugins validate ./plugins/microsoft-graph-security
hermes plugins doctor ./plugins/microsoft-graph-security
hermes plugins list
```

`validate` and `doctor` are read-only and safe to run at any time.

**Rollback:**

```bash
hermes plugins disable microsoft-graph-security
hermes plugins uninstall microsoft-graph-security
```

---

## 5. Pi ✅ (runtime unverified)

**How it works:** Pi packages are ordinary npm packages or local directories.
The `pi` key in `package.json` declares resources; `pi.skills` points at the
skill directory. No extension is needed — this package is instruction-only.

**Try it with nothing installed:**

```bash
pi --no-session --no-approve --print --no-tools \
  -e ./plugins/microsoft-graph-security \
  "List the available Microsoft 365 security workflows."
```

**Project-local install (writes `.pi/settings.json`, needs project trust):**

```bash
pi install ./plugins/microsoft-graph-security -l
```

**Verify:** `pi list` shows the package. A real skill load needs a model call.

**Rollback:** `pi remove ./plugins/microsoft-graph-security -l`

**Honest limit:** the manifest and resource paths were verified statically. A
runtime load on this machine returned an external usage-limit error, so **a
successful Pi skill load is unproven here.** Report it as unverified.

---

## 6. OpenCode ✅

**How it works:** OpenCode reads project skills from `.opencode/skills/`,
`.claude/skills/` and `.agents/skills/`, and global skills from
`~/.config/opencode/skills/`, `~/.claude/skills/` and `~/.agents/skills/`.

**Install: none.** If `.agents/skills` already points at the canonical skills,
OpenCode finds them.

**Verify:**

```bash
opencode debug skill
```

**Trap — this will mislead you.** `opencode debug skill` prints **JSON with
every skill body inlined**, so `grep 'cloud-security-engineer'` returns
**zero** and looks like total failure. Count entries by location instead:

```bash
opencode debug skill | python3 -c \
  "import sys,json; print(sum('11-mcps' in s.get('location','') for s in json.load(sys.stdin)))"
```

Expect `19`.

**Rollback:** remove the project skill links; nothing else was written.

---

## 7. OpenClaw ✅ (installer written by this repo)

**How it works:** OpenClaw discovers workspace skills at
`<workspace>/skills/` and project agent skills at
`<workspace>/.agents/skills/`. MCP servers live under `mcp.servers` in
`openclaw.json`, which is **user-level** and is never written by this package.

**Install the skills (local, opt-in):**

```bash
bun run scripts/install-openclaw.ts --workspace "$PWD"
```

**Verify:** the command prints `created`, then `already linked` on a second run.
A real directory at the target is **refused**, never replaced.

**Rollback:**

```bash
bun run scripts/install-openclaw.ts --workspace "$PWD" --uninstall
```

**Then add the gateway yourself** to `mcp.servers` in your OpenClaw config,
using the entry in Part 3.

**Honest limit:** OpenClaw is not installed on the machine that wrote this
document, so `openclaw mcp doctor` was never run. The installer is tested; the
runtime is not.

---

## 8. Gemini CLI 📄 — deprecated

**Status:** Google has retired Gemini Code Assist for individuals. The CLI
refuses to authenticate:

> `IneligibleTierError: This client is no longer supported … migrate to the
> Antigravity suite of products`

It discovers **0** skills in that state. **Use Antigravity instead** — see
entry 2. Listed here only so you do not waste time on it.

---

## 9. Codex CLI 📄

**How it works:** Codex reads `AGENTS.md` for project context and supports MCP
servers. Vendor documentation also lists a Skills section, but the installed
`codex --help` on this machine does not mention skills, so **skill loading is
unverified here.**

**Do this:** point Codex at the gateway with the Part 3 config, and let it read
`AGENTS.md`-style project context. If skill support is present in your version,
symlink `skills/` into the location your version documents.

**Verify:** `codex mcp list` (or your version's MCP listing).

**Honest limit:** unverified locally. Report as such.

---

## 10. Cursor 📄

**How it works:** Cursor supports MCP servers and its own rules files. It is
**not** a documented Agent Skills host, so treat it as an MCP client plus, if
your version supports it, a rules file.

**Do this:** add the Part 3 MCP config to Cursor's settings.

**Verify:** the MCP server shows as connected in Cursor's MCP panel.

---

# Part 2 — Other MCP-capable agents

These can reach the gateway as an MCP server. They are listed so you know the
category; consult that host's own documentation for the exact settings file.

Cursor · Cline · Roo Code · Kilo Code · Continue · Windsurf · Warp · Aider ·
Crush (charmbracelet) · Amp (Sourcegraph) · Kiro (AWS) · Trae · Void · PearAI ·
Melty · Codebuff · Sweep · Junie (JetBrains) · Tabnine · Sourcegraph Cody ·
Qodo · Zed · Amazon Q Developer CLI · GitHub Copilot (CLI and IDE) ·
Claude Desktop · OpenHands · GPT Engineer · Jan · AnythingLLM · LobeChat ·
LibreChat · Open WebUI · 5ire · BoltAI · Firebase Studio · Jules · Replit Agent

### The one config they all share

MCP is the common denominator. This is the **verified** gateway entry from the
main repository — same shape everywhere:

```json
{
  "mcpServers": {
    "microsoft-graph": {
      "command": "bun",
      "args": ["run", "gateway_mcp/src/index.ts"]
    }
  }
}
```

**The relative path only works while your working directory is a clone of the
main repository.** If your MCP client launches servers from somewhere else, the
command fails with `Module not found`. Options, in order of preference:

1. Run the gateway as a compiled binary and point `command` at it.
2. Set an explicit working directory if your client supports one.
3. Accept an absolute path that you own and maintain.

Do **not** invent a path and hope. Test it: the gateway prints its
`initialize` response and the tenant it is connected to within a few seconds.

### Verifying any MCP client

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"check","version":"1"}}}' \
  | bun run gateway_mcp/src/index.ts
```

A valid `initialize` response naming `mcp-gateway` means the transport works.
The process stays running — that is expected. Stop it when you are done.

---

# Part 3 — If nothing above matches you

You are an **MCP client**. You cannot load these skills natively.

1. Add the Part 2 `mcpServers` entry to your client's MCP configuration.
2. Confirm the gateway starts using the verification command in Part 2.
3. Once the tools are listed, ask the gateway for `gateway://session` and state
   the tenant before doing anything else.
4. The workflow instructions are in this package's `skills/` directory. If your
   client can read files, point it at
   `plugins/microsoft-graph-security/skills/m365-security-workflows/SKILL.md` and
   let it route to the canonical skill. If it cannot, say so plainly — do not
   paraphrase a security procedure from memory.

---

## What this package is not

- It is **not** the server. The gateway lives in the main repository.
- It contains **no** credentials, tenant ids, or personal data.
- It installs **no** executable extension. Every host entry above is
  instructions and a manifest, nothing that runs on its own.

## If something is wrong

Report the host, the exact command, and the exact error. Do not work around a
failed safety check, a failed validator, or a blocked install to make it look
like it succeeded.
