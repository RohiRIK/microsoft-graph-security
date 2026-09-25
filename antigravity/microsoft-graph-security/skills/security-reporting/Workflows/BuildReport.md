# BuildReport

From findings to a workbook or HTML page a person can read.

## Step 1: Pin the scope

Restate in one line what the report covers and what it leaves out ("the 10 policies not named
Default Policy — not the Default ones"). If a scope word is ambiguous, ask before building.

## Step 2: Get the data

From the analysis skill's source — an MCP tool result, or a snapshot on disk (for DLP:
`~/.mcp-graph/snapshots/<tenant>/dlp-*.json`). Name the tenant (`gateway://session`).

## Step 3: Build the spec in a script

Write a short Python script in the **session scratchpad** that reads the data and emits the spec
JSON. Compute every number there. Use `Layouts.md` for the page set and `WritingRules.md` for the
words. Keep the spec out of the repo — it holds tenant data.

## Step 4: Render

```bash
python3 skills/security-reporting/scripts/render_report.py <spec.json> \
  --xlsx ~/Downloads/<Report>-<tenant>.xlsx --html ~/Downloads/<Report>-<tenant>.html
```

Excel when the user wants to edit, filter or forward; HTML when they want to read or present.
Both is cheap — same spec.

## Step 5: Read it back

Open the output (openpyxl for xlsx; the HTML text) and check: tab names, the first rows, totals,
and that labels match their data (the GLBA-was-filed-as-personal-data check). Fix the spec script,
re-render — never hand-edit the output.

## Step 6: Hand over

Path, what each page holds (one line each), that it names tenant users and groups, and that
nothing was changed in the tenant if it is a plan.

## Execution Log

```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"security-reporting","workflow":"BuildReport","status":"ok","duration_s":'$SECONDS'}' \
  >> ~/.claude/state/execution.jsonl
```
