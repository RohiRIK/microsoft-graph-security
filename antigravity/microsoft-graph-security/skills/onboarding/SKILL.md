---
name: onboarding
description: Getting someone from a fresh clone to a working connection, and unsticking them when a step fails. USE WHEN a person is setting this up for the first time, or hits an error during setup, bootstrap, doctor, or first connect. NOT FOR changing auth on a working install (use auth-ops).
metadata:
  category: workflow
  effort: low
  domain: onboarding
---

# Onboarding

`docs/QUICKSTART.md` is the path. This is what to do when someone is on it and stuck.

Your job is to get them to a passing `bun run doctor`, and nothing more. Resist
explaining the architecture — someone mid-setup is not asking how it works.

## The one question that decides everything

**Do they need unattended operation?**

- **No** (almost always) → delegated interactive. No app registration, no bootstrap,
  no administrator involved. Microsoft's own public client, and the server acts as
  them under their MFA and CA policy.
- **Yes** → app-only, which means bootstrap, a certificate, and an admin who has to
  consent.

People pick app-only because it sounds more professional. It is not; it is more work
and more standing access. If they have not said "unattended" or "scheduled", steer to
delegated and say why in one sentence.

## Errors, and what they actually mean

**The table lives in `docs/QUICKSTART.md` → "When something goes wrong".** Read it
there. A second copy here meant two documents to update whenever a message
changed, and the one nobody remembered would start lying.

Two things that table cannot say, because they are about how you behave rather
than what the person sees:

- **`AADSTS650053` is not solved by adding permissions.** One scope with no
  delegated form makes Entra reject the *entire* sign-in — 25 valid scopes lost
  to one invalid one. The fix is always removal, never addition, and never a
  request to an administrator.
- **`invalid_client` on the delegated path means the wrong path was chosen.** It
  is an app-only failure. Someone seeing it under `interactive` has an
  `accessMode: app_only` they did not intend — fix the mode, do not go and build
  an app registration they never needed.

When the message is on neither, `bun run doctor --json` prints everything it
checked. Read that before guessing.

## What you never do for them

These are `auth-ops` refusals and they apply here too — an onboarding conversation is
exactly where the pressure to be helpful is highest:

- Never grant admin consent. Print the URL; the human clicks it.
- Never widen `tenant.allowlist`. Add a profile, never a tenant.
- Never enable writes to "make it work". Read-only is the default on purpose.
- Never write a credential into a file.

Full rules: `skills/auth-ops/`.

## Before you say it is done

`bun run doctor` prints their tenant, their profile, and no failures. Not "it should
work now" — run it.

On the delegated path, `[warn] not verified` is not a failure; it means `--sign-in`
has not been run yet.

## Gotchas

- **`bun run cli` and the servers resolve settings differently — they did not used to.** If
  a command claims "No settings.yaml was found" while `bun run status` shows a profile, that
  was a real bug (fixed 2026-08-09); check the version before believing the message.
- **A running MCP client does not see a settings change.** Settings resolve once at startup.
  Someone who edits `settings.yaml` and retries in the same session is still on the old
  tenant — the gateway now refuses rather than serving it, but they must reconnect.
- **`AADSTS90072` is not a permissions problem.** The account signed in belongs to a
  different tenant than the profile names. Fix the account or the profile, never the allowlist.
- **`--sign-in` is the only command that opens a browser.** If anything else does, that is a
  bug worth reporting, not a step to click through.
