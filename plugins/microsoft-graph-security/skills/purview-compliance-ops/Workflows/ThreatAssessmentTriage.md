---
type: Workflow
title: "Threat Assessment Triage"
description: "Check status and staleness of a user-reported phishing/malware/content submission."
tags: [purview, threat-assessment, phishing]
timestamp: 2026-07-31T00:00:00Z
---

# Threat Assessment Triage

## Steps

1. `purview.list_threat_assessment_requests` — filter by category (mail/file/URL) or requester if known.
2. `purview.get_threat_assessment_request` — pull verdict, category, and submission timestamp for the matching request.
3. Compute days-open. Anything past 3 business days with no verdict is stale — say so explicitly, don't just report raw status.
4. If the request correlates with a live alert, hand off to Defender evidence gathering (`security-ops`'s SpearphishBlastRadius workflow covers the blast-radius side; this workflow only covers the submission's own disposition).

## Gotchas

- A "resolved" verdict doesn't mean remediated — cross-check with `security-ops`'s PhishingPurge workflow if the verdict was malicious and no purge has been recorded.
