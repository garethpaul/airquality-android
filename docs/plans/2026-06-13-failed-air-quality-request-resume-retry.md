---
title: Failed Air Quality Request Resume Retry
date: 2026-06-13
type: implementation-plan
---

# Failed Air Quality Request Resume Retry

Status: Completed

## Summary

Retain retry intent when a foreground air-quality request completes with no
JSON response, then retry once from the accepted location on the next activity
resume without introducing an automatic retry loop.

## Problem Frame

`NetworkRequest` returns `null` after transport, status, decoding, or JSON
failures. `MainActivity` currently converts that result to `Unknown`, clears
the request, and records no incomplete-work state. A later pause overwrites the
existing restart flag with `airQualityRequest != null`, which is already false,
so resume does not retry and location updates remain stopped.

## Requirements

- R1. Mark retry intent only when the current non-stale request callback
  receives a `null` response.
- R2. Preserve existing retry intent when pause also records whether it
  interrupted an active request.
- R3. Reuse the retained accepted location on resume and clear retry intent
  before dispatch so repeated failures do not create an immediate loop.
- R4. Clear retry intent after a successful response and during destruction.
- R5. Preserve request identity guards, pause cancellation, location cleanup,
  coordinate privacy, generic logs, and completed-result suppression.
- R6. Add mutation-sensitive SDK-free contracts and completed verification
  evidence for failure marking, pause preservation, success clearing, resume
  ordering, and teardown cleanup.

## Key Technical Decisions

- **Reuse the existing restart flag:** both pause-interrupted and failed work
  represent one pending resume-time request, so a second lifecycle flag would
  duplicate state.
- **Retry only on resume:** a failure marks incomplete work but does not
  recursively dispatch from the callback or create unbounded retries.
- **Preserve stale-callback ordering:** only the callback matching the active
  request may change retry state.

## Scope Boundaries

- Do not add immediate retries, backoff, background networking, or persistence.
- Do not change `NetworkRequest`, HTTP timeouts, response limits, or logging.
- Do not modernize `AsyncTask`, Apache HTTP, Gradle, Fabric, TwitterKit, or the
  target SDK.
- Do not claim emulator or physical-device behavior without execution evidence.

## Work Completed

- Marked resume-time retry intent when the current request returns no response,
  after stale, cancelled, finishing, and destroyed callback guards.
- Preserved existing retry intent when pause records an interrupted request by
  combining both conditions instead of overwriting the flag.
- Reused the existing resume path so retained locations retry once and the flag
  is cleared before dispatch; successful responses clear retry intent.
- Extended the SDK-free checker and project guidance with mutation-sensitive
  ordering, documentation, and completed-plan contracts.

## Verification Completed

- Local and external-working-directory `make check` passed Python compilation
  and all SDK-free contracts; Gradle truthfully skipped because the Android SDK
  is not configured in this Linux worktree.
- Hosted Python 3.10, 3.12, 3.14, and Android results are recorded separately
  in tracker evidence after push; this plan makes no pre-push hosted claim.
- Seven hostile mutations for lost retry marking, pause overwrite, success retention,
  stale callback ordering, teardown retention, documentation, and plan status
  were rejected
- Exact diff, generated-artifact, credential-pattern, coordinate-log, conflict,
  and whitespace inspection passed
