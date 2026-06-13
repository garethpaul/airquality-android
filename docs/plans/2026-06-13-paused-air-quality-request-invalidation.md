---
title: Paused Air Quality Request Invalidation
date: 2026-06-13
type: implementation-plan
---

# Paused Air Quality Request Invalidation

Status: Completed

## Summary

Invalidate and cancel an in-flight air-quality request when `MainActivity`
pauses, then restart only pause-interrupted work from the retained location on
resume without refreshing completed results.

## Problem Frame

The activity currently stops location and sensor listeners on pause but leaves
`airQualityRequest` active. Its callback can therefore publish state while the
activity is backgrounded. Cancelling that request without changing resume
behavior would also strand the retained location because resume only acquires
when `location` is null.

## Requirements

- R1. Clear the active request identity and cancel the superseded task before
  `onPause()` delegates to the superclass.
- R2. Keep the existing callback identity guard so a late completion from the
  paused task cannot clear or update current activity state.
- R3. Record whether pause interrupted an active request and restart only when
  no request is active and either location acquisition or that request remains
  incomplete.
- R4. Prefer the retained location for a resumed request; acquire a location
  only when none is retained.
- R5. Preserve successful state across pause/resume without starting a
  duplicate request.
- R6. Preserve location cleanup, destroy-time cancellation, sensor behavior,
  generic logs, coordinate privacy, timeout/response limits, and the legacy
  Android SDK boundary.
- R7. Add mutation-sensitive SDK-free contracts and completed verification
  evidence for cancellation ordering, identity invalidation, resume retry, and
  successful-state suppression.

## Key Technical Decisions

- **Reuse request identity as the stale-callback guard:** setting
  `airQualityRequest` to null before cancellation makes any later callback fail
  the existing `airQualityRequest != this` check without adding a new token.
- **Track interruption explicitly:** a lifecycle flag records only requests
  cancelled by pause, avoiding coupling request behavior to the display string
  or changing completed-failure behavior.
- **Reuse retained location:** a resumed incomplete request can dispatch from
  the already accepted coordinates without reopening provider listeners.

## Implementation Units

### U1. Invalidate Requests On Pause

- **Files:** `app/src/main/java/twitterdev/airquality/MainActivity.java`
- **Goal:** Add one request-cleanup helper used by pause and destroy paths that
  clears identity before cancellation, retaining the callback guard and exact
  teardown ordering.
- **Test scenarios:** Pausing with a request clears the field before cancel;
  pausing without a request is a no-op; a stale callback cannot publish state;
  destroy continues to cancel and clear active work.

### U2. Resume Only Unresolved Work

- **Files:** `app/src/main/java/twitterdev/airquality/MainActivity.java`
- **Goal:** Gate resume on no active request plus missing location or an
  explicit pause-interruption flag, dispatching from the retained location or
  falling back to location acquisition.
- **Test scenarios:** A pause-interrupted retained location restarts exactly
  once; missing location starts acquisition; active requests and completed
  results do not start duplicate work.

### U3. Preserve The Durable Contract

- **Files:** `scripts/check_airquality_android_contracts.py`, `README.md`,
  `SECURITY.md`, `VISION.md`, `CHANGES.md`,
  `docs/plans/2026-06-13-paused-air-quality-request-invalidation.md`
- **Goal:** Require pause ordering, identity invalidation, resume predicates,
  retained-location dispatch, stale callback protection, documentation, and
  completed verification evidence.
- **Verification:** SDK-free checker, local/external `make check`, hosted Android
  build when available, hostile mutations, exact-diff artifact/secret/location
  scans, and whitespace validation.

## Scope Boundaries

- Do not modernize `AsyncTask`, Apache HTTP, Gradle, Fabric, TwitterKit, target
  SDK, or runtime permissions.
- Do not add background networking, continuous refresh, persisted coordinates,
  or coordinate logging.
- Do not refresh a successful result solely because the activity resumed.
- Do not claim emulator or physical-device behavior without execution evidence.

## Verification

- The SDK-free checker requires pause-time invalidation before superclass
  delegation, request identity clearing before cancellation, retained-location
  resume, interruption gating, callback identity protection, and shared
  destroy/supersession cleanup.
- Local and external-working-directory `make check` passed Python compilation
  and all SDK-free contracts; Gradle truthfully skipped because no Android SDK
  is configured in this Linux worktree.
- Eleven focused hostile mutations were rejected across resume predicates,
  retained-location reuse, pause interruption recording, cancellation,
  identity clearing, callback guards, shared cleanup, documentation, and
  completed plan status.
- No location coordinates, credentials, live provider requests, emulator, or
  physical-device data are used by the SDK-free contracts.
