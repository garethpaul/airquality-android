# String Air Quality State Validation

status: completed

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
  lifecycle cancellation, location handling, sensor rendering, production
  dependencies, target SDK, or public backend contracts.
- A pinned test-only JSON implementation and its Maven Central resolver are in
  scope only to make the existing Android JVM tests execute real `JSONObject`
  behavior instead of Android SDK stub methods.
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

- Replaced `optString` coercion with a raw-value `String` type guard while
  preserving the existing null and blank fallback.
- Added `MainActivityTest` coverage for valid strings plus missing, null, blank,
  boolean, numeric, object, array, and null-response cases.
- Added SDK-free source, fixture, guidance, and completed-plan contracts.
- Updated maintained README, security, vision, and change guidance.

## Verification Completed

- `readAirQualityStateDefaultsMissingNullBlankAndNonStringValues` is registered
  in both Android JUnit coverage and the SDK-free static checker.
- `python3 -m py_compile scripts/check_airquality_android_contracts.py` passed.
- `make lint`, `make test`, `make build`, and `make check` passed from the
  repository; the complete check also passed through the absolute Makefile
  path from an external directory.
- Local Gradle and Android JUnit execution truthfully skipped because this
  Linux worktree has no Android SDK configuration; hosted Android verification
  remains required.
- Six isolated hostile mutations covering the raw-value read, string type
  guard, scalar and structured fixtures, maintained guidance, and plan status
  were rejected for their intended contracts.
- The simplification pass retained the direct raw-object guard and compact test
  helper as the clearest implementation.
- Plan-aware review found no actionable findings, and the exact eight-file
  diff, whitespace, generated-artifact, conflict-marker, build/workflow drift,
  and credential-shaped addition audits passed.

## Hosted Android Follow-Up

The first exact-head Android job ran the new tests and failed because local JVM
tests loaded the Android SDK's stub `org.json` classes. `JSONObject.put` and
`JSONObject.opt` throw the standard not-mocked runtime exception outside a
device, so the test process could not exercise the production type guard.

### Requirements

1. Add Maven Central as an application/test dependency resolver without
   removing the legacy repositories needed by the pinned Android toolchain.
2. Pin `org.json:json:20260522` as a test-only dependency. Maven Central marks
   it as the current release and its classes target Java 8 bytecode.
3. Keep the existing valid, missing, null, blank, boolean, numeric, object, and
   array assertions unchanged and executable in both debug and release JVM
   suites.
4. Add SDK-free contracts for the resolver, exact test dependency, and hosted
   correction evidence.
5. Run the complete Android gate locally with Java 8 and API 22, then require a
   new exact-head hosted result without weakening coverage.

### Verification Boundary

- The test-only library supplies executable JSON semantics; production Android
  continues using the platform `org.json` implementation.
- No emulator, physical device, live backend, location provider, or sensor is
  claimed by JVM test success.
