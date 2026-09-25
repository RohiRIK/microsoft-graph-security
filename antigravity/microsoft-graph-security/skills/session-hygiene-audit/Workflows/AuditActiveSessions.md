---
type: Workflow
title: "Audit Active Delegated Sessions"
description: "Check each package's token-cache config and file age, and disconnect stale sessions."
tags: [token-cache, session-audit]
timestamp: 2026-07-31T00:00:00Z
---

# Audit Active Sessions

## Steps

1. For each package in use (`entra_id_mcp`, `intune_mcp`, `defender_mcp`, `purview_mcp`), check its `.env`:
   - `<PREFIX>_ACCESS_MODE` — only `delegated` mode has a session to audit; `app_only` has none.
   - `<PREFIX>_TOKEN_CACHE` / `<PREFIX>_TOKEN_CACHE_PATH` — is caching even enabled?
   - `<PREFIX>_TOKEN_CACHE_MAX_AGE_HOURS` — configured TTL (default 24 if unset).
2. If a cache path is configured, check the file's actual mtime (`stat` or equivalent) — compare age against the configured TTL. If age exceeds TTL and the file still exists, that's a bug: the file-based expiry in `createFileCachePlugin` should have deleted it on the next access — flag for investigation rather than assuming it's fine.
3. For a long-running server process, the file mtime alone isn't the full picture — if you have visibility into the running process (logs, recent tool-call timestamps), reason about whether the in-memory `accountCachedAt` clock would also have expired by now.
4. **To force-end a session now** (handoff, suspected compromise of the local dev machine, end of a testing session): call `<namespace>.disconnect_session` where available (`entra`, `intune`). For `defender`/`purview` (no disconnect tool), delete the configured cache file directly and note that the *next* delegated call will require fresh sign-in.
5. Report: per-package access mode, cache config, current age vs TTL, and any action taken.

## Gotchas

- Don't call `disconnect_session` speculatively on every audit — it forces a fresh interactive/device-code sign-in on the next call, which is disruptive if the session is still legitimately in use. Only disconnect when there's a real reason (handoff, staleness bug, suspected compromise).
- A missing cache file is not itself a finding — it just means no session is currently cached (either never signed in, or already expired/disconnected). Report it as "no active session," not as an error.
