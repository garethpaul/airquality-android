# Location-Gated Air-Quality Request

Status: Completed

## Context

`MainActivity` currently starts `NetworkRequest` immediately after asking for a
location. When neither provider has a last-known value, the request uses the
fields' implicit `0.0,0.0` defaults, while the later `onLocationChanged`
callback is empty. The app can therefore display air quality for the Gulf of
Guinea instead of the device and keep unnecessary location updates registered.

## Requirements

- Do not start an air-quality request until a non-null Android `Location` is
  available.
- Start from a valid last-known location when present; otherwise wait for
  `onLocationChanged` and launch from that callback.
- Update the retained location and coordinate fields before launching the
  request.
- Stop location updates after acquiring a usable location, when the activity
  pauses, and before destruction.
- Resume location acquisition when the activity returns without a location or
  active request.
- Preserve request identity guards, cancellation, teardown checks, timeout and
  response limits, sensor behavior, generic logs, and the legacy SDK boundary.
- Add mutation-sensitive SDK-free contracts for request gating, callback
  ordering, listener cleanup, and completed verification evidence.

## Implementation Units

### U1: Centralize Request Launch

**Files:** `app/src/main/java/twitterdev/airquality/MainActivity.java`

Extract request construction into a location-taking helper. The helper records
the location and coordinates, stops location updates, cancels any superseded
request, installs the existing guarded completion callback, and executes with
the recorded coordinates. A null location returns without creating a request.

### U2: Connect Activity And Location Lifecycles

**Files:** `app/src/main/java/twitterdev/airquality/MainActivity.java`

Remove unconditional startup from `onCreate`. On resume, acquire a location
only when no location or request is retained. Route `onLocationChanged` through
the helper. Stop updates on pause and destroy without weakening request
teardown.

### U3: Enforce And Document The Contract

**Files:** `scripts/check_airquality_android_contracts.py`, `README.md`,
`SECURITY.md`, `VISION.md`, `CHANGES.md`,
`docs/plans/2026-06-13-location-gated-air-quality-request.md`

Require null gating, coordinate assignment and cleanup before execution,
callback delegation, pause/destroy cleanup, regression documentation, and
completed verification evidence.

## Scope Boundaries

- Do not modernize `AsyncTask`, Apache HTTP, Gradle, Fabric, TwitterKit, target
  SDK, or runtime permissions in this unit.
- Do not persist or log coordinates.
- Do not add continuous location refresh or background tracking.
- Do not claim emulator or physical-device behavior without execution evidence.

## Verification Plan

- Run the SDK-free checker and focused hostile mutations first.
- Run the full local `make check` gate and the same gate externally.
- Run the configured Gradle test/lint/assemble gate when the local SDK permits.
- Run Python compilation, `git diff --check`, artifact scans, and added-line
  secret/location-detail scans.
- Record hosted evidence only after exact-head checks complete.

## Verification

- `python3 scripts/check_airquality_android_contracts.py` reached only the
  expected incomplete-plan assertion before this status was updated.
- Ten focused hostile mutations were rejected for null gating, resume
  acquisition, startup ordering, both coordinate assignments, pre-cleanup
  execution, superseded cancellation, callback delegation, pause cleanup, and
  destroy cleanup.
- Local `make check` passed, including Python compilation and the SDK-free
  contract suite; Gradle was truthfully skipped because no Android SDK is
  configured in the worktree.
- An isolated external copy passed the same `make check` gate with the same
  explicit Android SDK skip.
- `git diff --check`, generated-artifact inspection, and added-line secret and
  coordinate-log scans passed. Hosted exact-head checks remain pending push.
