# MainActivity Sensor Event Guard

## Status: Completed

## Context

`MainActivity` now guards accelerometer registration, but the sensor callback
still assumed every event had a sensor, at least three axis values, and live UI
views. A malformed callback or stale layout could crash before the app shows the
air-quality state.

## Objectives

- Preserve accelerometer-driven air-quality rendering for valid events.
- Ignore null or malformed sensor events before reading `event.values`.
- Guard display views before updating images or text.
- Keep SDK-free static checker coverage for the behavior.

## Work Completed

- Added an `onSensorChanged` guard for null events, null sensors, null values,
  and too-short values arrays.
- Added a `displayAccelerometer` guard for missing `logo` or `text` views.
- Logged non-sensitive warnings for ignored sensor events and missing views.
- Extended `scripts/check_airquality_android_contracts.py`.
- Updated README, VISION, and CHANGES.

## Verification

- `python3 scripts/check_airquality_android_contracts.py`
- `make check`
- `git diff --check`

On this workspace, `make check` reported `Android SDK not configured; skipping
Gradle build`.

## Follow-Up Candidates

- Add JVM or Robolectric coverage for sensor event handling in a modernized
  test stack.
- Update coordinates on `onLocationChanged` before issuing follow-up backend
  requests.
