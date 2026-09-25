---
type: Workflow
title: "eDiscovery Case Review"
description: "Summarize an eDiscovery case's status, custodians, searches, and review sets."
tags: [purview, ediscovery]
timestamp: 2026-07-31T00:00:00Z
---

# Ediscovery Case Review

## Steps

1. `purview.list_ediscovery_cases` — find the case by name if the ID isn't known.
2. `purview.get_ediscovery_case` — pull status (active/closed), created/closed dates.
3. `purview.list_ediscovery_custodians` — who's held, and since when.
4. `purview.list_ediscovery_noncustodial_data_sources` — shared mailboxes/sites held.
5. `purview.list_ediscovery_searches` + `purview.list_ediscovery_review_sets` — what's been searched, what's queued for review.
6. Summarize: case status, custodian count, non-custodial source count, search/review-set progress. Flag `HOLD_GAP` if the case is active but a named custodian from the request is missing from step 3.

## Capability boundaries

- No tool applies or releases a hold, adds a custodian, or closes a case — all of that is a manual Purview portal / eDiscovery (Premium) action. Report findings, don't imply the skill acted.
