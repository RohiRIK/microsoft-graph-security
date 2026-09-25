---
type: Workflow
title: "Compare DLP Policies"
description: "After a merged DLP policy has run in simulation, check it catches what the policies it replaces catch — per location and per data type — and hand the client a plain report."
tags: [purview, dlp, data-loss-prevention, simulation, report]
timestamp: 2026-09-24T00:00:00Z
---

# Compare DLP Policies

> Is it safe to switch the new policy on and retire the old ones? Read-only; the answer is advice,
> the switch is a separate, confirmed step.

## Steps

1. **Name the tenant.** `gateway://session`.
2. **Fresh data.** `purview.start_dlp_export` with `days` covering the simulation (1–30), then
   `dlp_job_status` until done. Snapshots exported before 2026-09-24 have no per-type data.
3. **Compare.** `purview.compare_dlp_policies` with the `plan_id` the new policy was created from
   (the plan knows the new policy and its sources; plans are read here regardless of age), or
   `new_policy` + `old_policies`. Optional `since` (default: the day after the new policy's first
   match — go-live day is partial), `tolerance_pct` (default 10), `min_days` (default 7).
4. **Read the verdict out:**
   - **ready** — email and devices about the same, SharePoint/OneDrive the same or more, no data type
     missing. Suggest: switch on, turn the old ones off, delete them two weeks later.
   - **not ready** — name each location with fewer matches and each missing data type. Suggest: fix
     the rule (plan → dry run → create), let it run, compare again.
   - **too early** — under `min_days` full days: the numbers are a first look, no judgment yet.
   - **no data** — the new policy has recorded nothing yet; wait and export again.
5. **The client's report — to `~/Downloads`, never the repo:**
   ```
   bun run cli purview dlp compare --plan <plan-id> > "$TMPDIR/cmp.json"
   python3 skills/security-reporting/scripts/dlp_compare_spec.py "$TMPDIR/cmp.json" > "$TMPDIR/cmp.spec.json"
   python3 skills/security-reporting/scripts/render_report.py "$TMPDIR/cmp.spec.json" \
     --xlsx ~/Downloads/DLP-comparison-<tenant>.xlsx --html ~/Downloads/DLP-comparison-<tenant>.html
   ```
   Pages: the answer · by location · by data type (problems first) · old policies · next steps ·
   decisions. Read it back before handing it over (security-reporting → BuildReport step 5).

## Gotchas

- **SharePoint/OneDrive "more" is expected.** Simulation scans existing files; the old policies saw
  only new activity. Only "fewer" there is a problem.
- **Counts, not items.** The snapshot keeps counts per rule, location, day and data type id — never
  which email or file. "About the same" is a count comparison, which is why the window should be
  one to two weeks, not a day.
- **Compare the same full days.** The window starts the day after the new policy first matched (it
  went live part-way through that day, still rolling out); old matches before that are not counted.
  On the first real run, day one alone read "fewer everywhere" — that is why.
