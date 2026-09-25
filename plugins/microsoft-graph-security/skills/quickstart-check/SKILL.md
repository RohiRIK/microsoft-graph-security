---
name: quickstart-check
description: Proving docs/QUICKSTART.md still works before a release or after changing any command it names. USE WHEN setup, doctor, bootstrap, or a CLI flag changed, or before publishing. NOT FOR helping a person through setup (use Onboarding).
metadata:
  category: verification
  effort: low
  domain: onboarding
---

# quickstart-check

An onboarding document is worthless the first time it is wrong, and it goes wrong
silently — nobody re-reads it, so the rot is discovered by the one person it was
written for, at the worst moment.

Run this whenever a command the quickstart names has changed.

## The mechanical half

```bash
bun run rehearse
```

Clones into a temp directory with `HOME` redirected and `MCP_SETTINGS=none`, then
walks the quickstart's commands. It fails on anything that only works because of
state already on your machine.

**The isolation is the test.** `findSettingsFile` walks *upward*, so a clone made
beneath this repo inherits its `settings.yaml` and a real client tenant — and would
pass while the same steps failed for someone with an empty disk. If you change
`rehearse.ts`, do not weaken that.

It stops where a real tenant would be required. Everything past that point needs a
credential nobody should hand a rehearsal.

## The half a script cannot do

`bun run rehearse` proves the commands run. It cannot tell you a step is confusingly
worded, which is most of what makes onboarding fail. Read the document as well, and
check:

1. **Every command in it appears in the repo.** Grep each one. A flag that was renamed
   is the most common rot.
2. **The delegated/app-only fork is still unmissable.** It is the decision that costs
   the most when taken wrongly.
3. **The error table still matches reality.** Messages change, and the table in
   `docs/QUICKSTART.md` quotes them. It is the only copy — `skills/Onboarding/`
   points at it rather than restating it — so there is one place to fix.
4. **Nothing was added that is not on the path.** The document has one job: clone to
   passing `doctor`. Architecture, feature tours and rationale belong in README.

## Platform honesty

The quickstart states that only macOS is verified. If you have actually run a path on
Windows or Linux, update that line — and if you have not, do not.

## Definition of done

`bun run rehearse` exits 0, and every command in `docs/QUICKSTART.md` exists in the
repo. If the document changed, `git diff docs/QUICKSTART.md` should be readable as
instructions, not as prose about instructions.

## Gotchas

- **The isolation is the test.** `findSettingsFile` walks *up*, so a clone made beneath this
  repo inherits its `settings.yaml` and a real tenant, and every step passes while proving
  nothing. If you weaken `cleanEnv` in `rehearse.ts`, the harness keeps reporting green.
- **An uncommitted doc does not exist.** `rehearse` clones, so a QUICKSTART edit that has not
  been committed is invisible to it — that is correct, and it is the first thing to check
  when the doc step fails.
- **A passing rehearsal says nothing about wording.** It proves the commands run. Whether a
  step is followable is only answerable by a person who has not seen the repo.
