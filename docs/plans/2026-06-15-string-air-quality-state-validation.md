# String Air Quality State Validation

status: in progress

## Context

`MainActivity.readAirQualityState` uses `JSONObject.optString`, which coerces
JSON booleans, numbers, arrays, and objects into Java strings. Malformed backend
data can therefore replace the safe `Unknown` fallback with values such as
`true`, `42`, or serialized JSON and flow into accelerometer-driven UI state.

## Priorities

1. **P0: Require a string `air_quality` value.** Non-string JSON must retain the
   safe fallback instead of being coerced into display state.
2. **P1 follow-up: Decide whitespace normalization policy.** Review separately
   whether padded but otherwise valid states should be trimmed or rejected.
3. **P2 follow-up: Modernize state rendering.** Replace binary Good/bad display
   assumptions only as a dedicated product and UI change.

This plan implements only P0.

## Requirements

- Return `Unknown` when the response is null, the field is absent or null, the
  field is not a JSON string, or the string is blank.
- Preserve valid nonblank string values, the null-safe `Good` comparison,
  request identity and lifecycle guards, retry behavior, and UI resources.
- Add Android unit coverage for valid strings plus boolean, numeric, object,
  array, JSON-null, missing, blank, and null-response cases.
- Add mutation-sensitive source, test, documentation, and completed-plan
  contracts to the SDK-free checker.

## Scope Boundaries

- Do not change network transport, JSON body parsing, request retries,
  lifecycle cancellation, location handling, sensor rendering, dependencies,
  Gradle, target SDK, or public backend contracts.
- Do not claim emulator or physical-device behavior without execution evidence.

## Implementation Units

### U1: Require a string response state

**Files:** `app/src/main/java/twitterdev/airquality/MainActivity.java`,
`app/src/test/java/twitterdev/airquality/MainActivityTest.java`

**Approach:** Read the raw `air_quality` value, require `instanceof String`, and
apply the existing blank-value fallback before returning it. Add focused unit
tests that make every coercible non-string type observable as `Unknown` while
preserving `Good` and other nonblank strings.

**Execution note:** Test-first using synthetic `JSONObject` values only.

**Verification:** Android unit tests prove non-string values cannot become UI
state and valid strings retain current behavior.

### U2: Keep SDK-free contracts and guidance synchronized

**Files:** `scripts/check_airquality_android_contracts.py`, `README.md`,
`SECURITY.md`, `VISION.md`, `CHANGES.md`,
`docs/plans/2026-06-15-string-air-quality-state-validation.md`

**Approach:** Register the raw-value type guard, malformed-type fixtures,
maintained guidance, and completed-plan evidence in the Python checker used on
hosts without an Android SDK.

**Verification:** Isolated mutations to the type guard, representative scalar
and structured fixtures, documentation, and completed-plan status are rejected.

## Verification Plan

- Run the focused Android unit test when the SDK is available and the SDK-free
  contract checker on every host.
- Run every documented Make gate from the repository root and the complete
  check through the absolute Makefile path from an external directory.
- Run isolated hostile mutations for source, test, documentation, and plan
  contracts.
- Audit the exact intended diff, generated artifacts, conflict markers,
  credential-shaped additions, and whitespace before committing.

## Work Completed

Pending implementation.

## Verification Completed

Pending implementation and validation.
