#!/usr/bin/env python3
"""Turn a DLP comparison (from `bun run cli purview dlp compare`) into a report spec.

    bun run cli purview dlp compare --plan <plan-id> > /tmp/cmp.json
    python3 skills/security-reporting/scripts/dlp_compare_spec.py /tmp/cmp.json > /tmp/cmp.spec.json
    python3 skills/security-reporting/scripts/render_report.py /tmp/cmp.spec.json \
        --xlsx ~/Downloads/DLP-comparison-<tenant>.xlsx --html ~/Downloads/DLP-comparison-<tenant>.html

Generic: every name and number comes from the comparison file, so nothing about a client lives
here. The output names the tenant's policies and belongs in ~/Downloads, never in the repo.
Plain words per WritingRules.md: the answer on page 1, what users notice, decisions as questions.
"""

from __future__ import annotations

import json
import sys

ANSWER = {
    "ready": "Ready: the new policy catches what the old policies catch.",
    "not_ready": "Not ready: the new policy misses things the old policies catch.",
    "too_early": "Too early: not enough full days yet to judge — the numbers are a first look.",
    "no_data": "No data yet: the new policy has not recorded anything to compare.",
}
LOCATION_RESULT = {
    "ok": "About the same ✓",
    "fewer": "FEWER — the new policy misses matches",
    "more": "More — check it is not noise",
    "no_data": "No matches in either",
}
TYPE_RESULT = {
    "ok": "Caught by both ✓",
    "missing": "MISSING — never matched in the new policy",
    "fewer": "Fewer in the new policy — review",
    "new_only": "Only in the new policy (often existing files)",
}
EXPECT = {"same": "About the same", "same_or_more": "Same or more (simulation also scans existing files)"}
TYPE_ORDER = {"missing": 0, "fewer": 1, "new_only": 2, "ok": 3}


def build(c: dict) -> dict:
    tenant = c.get("tenantName") or c.get("tenantId", "")
    window = c["window"]
    when = f"{window.get('from') or '—'} to {window.get('to') or '—'} ({window['days']} day(s))"
    old_n = len(c["oldPolicies"])
    verdict = c["verdict"]

    means = {
        "ready": [
            "Switch the new policy from simulation to on.",
            f"Then turn off the {old_n} old policies, and delete them two weeks later.",
            "Users notice nothing while it only records; they would notice blocking only if a rule blocks.",
        ],
        "not_ready": [
            "Do not switch yet. Fix the rules that miss matches (a new plan, dry run and create).",
            "Compare again after the fix has run.",
        ],
        "too_early": ["Nothing to decide yet. Let the simulation run at least a week, then compare again."],
        "no_data": ["Let the simulation run, export a fresh snapshot, and compare again."],
    }[verdict]

    summary = {
        "type": "summary",
        "name": "The answer",
        "before_after": {
            "before_label": "OLD POLICIES", "before_value": c["totals"]["oldMatches"],
            "before_caption": f"matches, {old_n} policies",
            "after_label": "NEW POLICY", "after_value": c["totals"]["newMatches"],
            "after_caption": "matches, in simulation",
        },
        "sections": [
            {"heading": "The answer", "callout": True, "text": ANSWER[verdict]},
            {"heading": "Why", "bullets": c["reasons"] or ["No differences worth noting."]},
            {"heading": "What it means", "bullets": means},
            {"heading": "Compared", "bullets": [
                f"New policy: {c['newPolicy']}",
                f"Old policies: {', '.join(c['oldPolicies'])}",
                f"Period: {when}",
                "Nothing has been changed in the tenant.",
            ]},
        ],
    }

    locations = {
        "type": "table", "name": "By location",
        "title": "Where the matches happened",
        "subtitle": "Email and laptops see the same traffic either way; SharePoint and OneDrive should show the same or more.",
        "headers": ["Location", "Old policies", "New policy", "What we expect", "Result"],
        "widths": [24, 14, 14, 44, 38],
        "rows": [[l["location"], l["oldMatches"], l["newMatches"], EXPECT[l["expectation"]], LOCATION_RESULT[l["verdict"]]]
                 for l in c["locations"]],
    }

    types_sorted = sorted(c["types"], key=lambda t: (TYPE_ORDER[t["verdict"]], -t["oldMatches"], t["name"]))
    types = {
        "type": "table", "name": "By data type",
        "title": "Each data type, problems first",
        "headers": ["Data type", "Old policies", "New policy", "Result"],
        "widths": [52, 14, 14, 44],
        "rows": [[t["name"], t["oldMatches"], t["newMatches"], TYPE_RESULT[t["verdict"]]] for t in types_sorted]
        or [["No per-type data in this snapshot — export again", "", "", ""]],
    }

    olds = {
        "type": "table", "name": "Old policies",
        "title": "The old policies in this period",
        "headers": ["Old policy", "Matches", "After the switch"],
        "widths": [60, 12, 36],
        "rows": [[p["policy"], p["matches"], "Turn off; delete 2 weeks later"] for p in c["oldByPolicy"]],
    }

    steps = {
        "type": "steps", "name": "Next steps",
        "headers": ["Step", "What", "What users notice", "How long"],
        "widths": [7, 72, 22, 12],
        "rows": (
            [[1, "Switch the new policy from simulation to on", "Nothing (it only records)", "1 day"],
             [2, "Turn off the old policies", "Nothing", "1 day"],
             [3, "Wait two weeks in case we need to roll back, then delete the old policies", "Nothing", "2 weeks"]]
            if verdict == "ready" else
            [[1, "Fix the rules that miss matches (new plan → dry run → create)", "Nothing", "1 day"],
             [2, "Let it run, export again, compare again", "Nothing", "1–2 weeks"]]
            if verdict == "not_ready" else
            [[1, "Let the simulation run", "Nothing", "1–2 weeks"],
             [2, "Export a fresh snapshot and compare again", "Nothing", "1 day"]]
        ),
    }

    decisions = {
        "type": "decisions", "name": "Decisions",
        "title": "Decisions needed",
        "headers": ["#", "Question", "Suggestion", "Your answer"],
        "widths": [5, 60, 44, 26],
        "rows": [
            [1, "Switch the new policy on?", "Yes" if verdict == "ready" else "Not yet", ""],
            [2, f"Turn off the {old_n} old policies after the switch?", "Yes, keep them two weeks before deleting", ""],
        ],
    }

    return {
        "title": f"DLP comparison — {tenant}",
        "short_title": "DLP comparison",
        "subtitle": f"{c['newPolicy']} against the policies it replaces · {when}",
        "pages": [summary, locations, types, olds, steps, decisions],
    }


SAMPLE = {  # invented — Contoso
    "tenantName": "Contoso", "newPolicy": "Merged policy", "oldPolicies": ["Old A", "Old B"],
    "window": {"from": "2026-01-01", "to": "2026-01-14", "days": 14}, "typesRecorded": True,
    "locations": [{"location": "Exchange", "expectation": "same", "oldMatches": 100, "newMatches": 60, "verdict": "fewer"}],
    "types": [{"id": "a", "name": "Passport Number", "oldMatches": 5, "newMatches": 5, "verdict": "ok"},
              {"id": "b", "name": "Credit Card Number", "oldMatches": 40, "newMatches": 0, "verdict": "missing"}],
    "oldByPolicy": [{"policy": "Old A", "matches": 100}], "totals": {"oldMatches": 100, "newMatches": 60},
    "verdict": "not_ready", "reasons": ["Exchange: fewer"],
}


def selftest() -> None:
    spec = build(SAMPLE)
    names = [p["name"] for p in spec["pages"]]
    assert names == ["The answer", "By location", "By data type", "Old policies", "Next steps", "Decisions"], names
    assert spec["pages"][2]["rows"][0][0] == "Credit Card Number", "problems must come first"
    assert spec["pages"][0]["sections"][0]["text"].startswith("Not ready"), "page 1 gives the answer"
    for verdict in ("ready", "too_early", "no_data"):
        build({**SAMPLE, "verdict": verdict})
    print("dlp_compare_spec selftest: ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
        sys.exit(0)
    if len(sys.argv) != 2:
        sys.exit("usage: dlp_compare_spec.py <comparison.json>  (from: bun run cli purview dlp compare ...)")
    with open(sys.argv[1], encoding="utf-8") as f:
        text = f.read()
    start = text.find("{")  # tolerate a leading `$ bun run ...` line from the root CLI wrapper
    json.dump(build(json.loads(text[start:])), sys.stdout, ensure_ascii=False, indent=1)
