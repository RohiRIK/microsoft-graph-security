---
name: security-reporting
description: Turn findings from any Microsoft 365 plane (DLP, Entra, Intune, Defender, Exchange, Purview) into a plain-language Excel workbook and/or a self-contained HTML page — an inventory, a clean-up or merge plan, steps, and decisions — for people, not for analysts. USE WHEN asked for an Excel/xlsx, spreadsheet, HTML page, report, plan, or "write this up" from MCP findings or a snapshot. NOT FOR the analysis itself (use purview-compliance-ops, defender-posture-reporting, cloud-security-engineer) or for publishing a page online (tenant data stays local).
metadata:
  category: workflow
  effort: medium
  domain: security
---

# security-reporting

The analysis skills find things; this one explains them to a person. One JSON **spec** describes
the pages; `scripts/render_report.py` turns it into an Excel workbook, an HTML page, or both —
same pages, same plain style, no new builder script per report.

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **BuildReport** | "put this in Excel", "make an xlsx / HTML", "write up the plan", "inventory of …" | `Workflows/BuildReport.md` |

## Quick Reference

- Writing rules (read first): `WritingRules.md`. Page types and which to use: `Layouts.md`.
- Render: `python3 scripts/render_report.py spec.json --xlsx out.xlsx --html out.html`
- Check the renderer: `python3 scripts/render_report.py --selftest`
- Worked example (invented data): `examples/merge-plan.spec.json`.
- DLP comparison report: `scripts/dlp_compare_spec.py <comparison.json>` builds the spec from
  `bun run cli purview dlp compare` output (purview-compliance-ops → CompareDlpPolicies).
- Output goes to `~/Downloads/` (or where the user says) — **never the repo**, never an online page.

## Gotchas

- **Answer the scope that was asked, nothing wider.** "Check the old policies" meant an inventory
  of the old ones — not a redesign, and not the new ones. When a scope word is used (old, new,
  existing, only), build exactly that and offer the rest in one line.
- **Ask what the user's words mean when they name a group.** In one tenant "old" meant "every
  policy not named *Default Policy*" — a naming convention no data field records.
- **Every number comes from data, computed in the script that builds the spec.** Never type a
  count by hand. Then read the rendered file back and check the numbers add up before handing it
  over (a total row that does not equal its rows is the tell).
- **Read the labels back, too.** A category that reads fine in code can be wrong in words — GLBA
  was filed under "personal data" until the read-back showed it is US *financial* data.
- **Tenant data never goes to git or to a published page.** Reports name users, groups and
  policies. Save locally; the repo gets only the spec *format* and invented examples.
- **Deleting an earlier output is the user's call.** Replace a file only when asked; otherwise
  write a new name.
- **openpyxl is a Python dependency** (`pip install openpyxl`). HTML needs only the standard
  library, so HTML still works where openpyxl is missing — the selftest says which.
- **Excel is the reader, LibreOffice is not required.** The renderer writes values, not formulas,
  so nothing needs recalculating. If a formula is genuinely needed, see the `xlsx` skill.

## Examples

```
User: "Put the old DLP policies in an Excel"
→ BuildReport → inventory spec (summary + table + appendix table) from the latest snapshot
→ render --xlsx ~/Downloads/DLP-old-policies-<tenant>.xlsx → read back → report

User: "Now a plan to merge them, as HTML too"
→ BuildReport → summary + flow + table + steps + decisions → render --xlsx --html
```
