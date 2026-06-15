# Canonical Air Quality State Whitespace

status: completed

## Context

`MainActivity.readAirQualityState` uses `trim()` to detect blank strings but
returns the original value. A backend value such as `" Good "` is accepted as
nonblank yet fails the UI's exact `Good` comparison and renders the wrong
state.

## Requirements

- Trim surrounding whitespace from accepted string `air_quality` values.
- Continue returning `Unknown` for null responses, missing/null fields, blank
  strings, and non-string JSON values.
- Preserve request ownership, lifecycle guards, retry behavior, sensor
  rendering, resources, and the production JSON dependency boundary.
- Add real-JSON JVM coverage and mutation-sensitive SDK-free contracts.

## Scope Boundaries

- Do not change network transport, response parsing, location behavior,
  accelerometer behavior, dependencies, target SDK, or backend schema.
- Do not introduce case folding, state allowlisting, or new product states.
- Do not claim emulator, device, backend, location-provider, or sensor behavior
  without execution evidence.

## Implementation Units

### U1: Canonicalize accepted state strings

**Files:** `app/src/main/java/twitterdev/airquality/MainActivity.java`,
`app/src/test/java/twitterdev/airquality/MainActivityTest.java`

**Approach:** Store the trimmed string, use it for the blank check, and return
it. Extend the real `org.json` JVM test with padded `Good` and `Moderate`
values while retaining every malformed-value assertion.

**Verification:** `readAirQualityStateTrimsNonblankStrings` proves surrounding
whitespace cannot bypass exact UI state matching.

### U2: Keep SDK-free contracts and guidance synchronized

**Files:** `scripts/check_airquality_android_contracts.py`, `README.md`,
`SECURITY.md`, `VISION.md`, `CHANGES.md`,
`docs/plans/2026-06-15-canonical-air-quality-state-whitespace.md`

**Approach:** Register the single-trim source shape, real-JSON test values,
maintained guidance, and completed-plan evidence in the Python checker.

**Verification:** Isolated mutations to normalization, padded fixtures,
guidance, and completed-plan evidence are rejected.

## Verification Plan

- Run the focused debug and release JVM tests with the pinned real JSON
  implementation, plus the SDK-free checker.
- Run every documented Make gate from the repository root and the complete
  check through the absolute Makefile path from an external directory.
- Run isolated hostile mutations for source, test, guidance, and plan
  contracts.
- Audit the exact intended diff, generated artifacts, project/dependency drift,
  conflict markers, credential-shaped additions, and whitespace.

## Work Completed

- Trimmed accepted string `air_quality` values once before blank detection and
  return.
- Added `readAirQualityStateTrimsNonblankStrings` with padded `Good` and
  `Moderate` values using the pinned real JSON implementation.
- Registered normalization, fixtures, maintained guidance, and completed-plan
  evidence in the SDK-free checker.

## Verification Completed

- Focused debug and release `MainActivityTest` JVM suites passed with Java 8,
  Android API 22, and `org.json:json:20260522`.
- The SDK-free Python checker and syntax compilation passed.
- `make check`, `make lint`, `make test`, and `make build` passed with the
  configured Android SDK; the complete check also passed through the absolute
  Makefile path from an external directory.
- Six isolated hostile mutations covering normalization, both padded fixtures,
  focused-test identity, guidance, and plan evidence were rejected.
- No emulator, device, backend, location-provider, or sensor behavior was
  exercised.
- Exact diff, generated-artifact, project/dependency, conflict-marker,
  credential-shaped addition audits, and whitespace checks are completed before
  commit.
